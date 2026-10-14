"""Lease-protected automatic recovery for interrupted forwarding tasks."""

import asyncio
import logging
from datetime import datetime, timezone

from config import temp
from database import db
from plugins.regix import (
    IND_SYS_CLIENT,
    execute_batch_forward,
    execute_single_copy,
    extract_media_id,
    format_custom_caption,
)
from plugins.test import parse_buttons, start_clone_bot
from plugins.utils import STS

logger = logging.getLogger(__name__)
RECOVERY_BATCH_SIZE = 50


def next_source_message_id(checkpoint_message_id):
    """The iterator's offset is exclusive: recovery begins at checkpoint + 1."""
    return max(0, int(checkpoint_message_id or 0))


def final_task_status(counts):
    """A task with any confirmed delivery failures is not reported as clean success."""
    return "completed_with_errors" if int((counts or {}).get("failed", 0)) else "completed"


def retry_delay_seconds(attempt):
    """Bounded exponential delay for worker-level failures."""
    return min(300, 5 * (2 ** max(0, int(attempt) - 1)))


async def _notify(bot, owner_id, message):
    try:
        await bot.send_message(int(owner_id), message, disable_web_page_preview=True)
    except Exception:
        logger.exception("Could not notify task owner %s", owner_id)


async def _flush_batch(node_client, batch_ids, task, state):
    if not batch_ids:
        return
    sent = await execute_batch_forward(
        node_client, list(batch_ids), None, state, task.get("protect_content")
    )
    for message_id in batch_ids:
        await db.checkpoint_forwarding_message(
            task["task_id"],
            message_id,
            "forwarded" if sent else "failed",
            None if sent else "batch forward failed after retries",
        )
    if sent:
        state.add("total_files", len(batch_ids))


async def recover_forwarding_task(bot, task):
    """
    Resume one task after claiming its MongoDB lease. The cursor is an exclusive
    source message ID boundary, not an item count or Pyrogram offset.
    """
    task_id = str(task["task_id"])
    owner_id = int(task["owner_id"])
    source = task.get("source_chat_id")
    destination = task.get("destination_chat_id")
    node_id = task.get("active_node_id")
    lease_owner = task.get("lease_owner")

    if lease_owner != db.worker_id:
        logger.warning("Refusing task %s: lease is no longer owned by this process", task_id)
        return

    if source is None or destination is None or node_id is None:
        await db.update_forwarding_task(task_id, {
            "status": "needs_attention",
            "last_error": "Task is missing its source, destination, or registered node ID.",
        })
        await _notify(bot, owner_id, f"Forwarding task {task_id} needs attention: saved task settings are incomplete.")
        return

    # A user's existing task takes priority over recovery. Release this claim
    # briefly rather than running two jobs for the same owner.
    if temp.lock.get(owner_id) or destination in temp.IS_FRWD_CHAT:
        await db.defer_forwarding_task(task_id, delay_seconds=15)
        return

    active_node = await db.get_node_for_task(owner_id, node_id)
    if not active_node:
        await db.update_forwarding_task(task_id, {
            "status": "needs_attention",
            "last_error": "The originally selected Telegram node is no longer registered for this owner.",
        })
        await _notify(
            bot, owner_id,
            f"Forwarding task {task_id} needs attention. Its previously selected bot/user session "
            "is no longer registered. Re-add that node before starting a new task.",
        )
        return

    # Reconcile counters from the idempotent outcome ledger. This also repairs the
    # rare crash window between inserting an outcome and updating its task counters.
    counts = await db.get_forwarding_outcome_counts(task_id)
    counts["processed"] = counts["forwarded"] + counts["skipped"] + counts["failed"]
    await db.update_forwarding_task(task_id, {"counts": counts})

    cursor = next_source_message_id(task.get("last_confirmed_message_id", task.get("cursor_message_id", 0)))
    limit = int(task.get("limit") or 0)
    original_skip = int(task.get("skip") or 0)

    session_id = task.get("transmission_id") or task_id
    state = STS(session_id).store(source, destination, original_skip, limit)
    state_data = state.get()
    state_data["fetched"] = cursor
    state_data["total_files"] = int(counts.get("forwarded", 0))
    state_data["deleted"] = int(counts.get("failed", 0))
    state_data["duplicate"] = int(counts.get("skipped", 0))
    state_data["start"] = __import__("time").time()

    # Settings are captured at task creation so a later settings change does not
    # silently change the semantics of a long-running task. Older task records do
    # not have a snapshot, so use the owner's current button/caption as a fallback.
    button_payload = task.get("button_payload")
    caption_template = task.get("caption_template")
    if "settings_snapshot" not in task:
        legacy_config = await db.get_configs(owner_id)
        if button_payload is None:
            button_payload = legacy_config.get("button")
        if caption_template is None:
            caption_template = legacy_config.get("caption")
    inline_button = parse_buttons(button_payload or "", markup=True)
    forward_tag = bool(task.get("forward_tag"))
    if temp.lock.get(owner_id) or destination in temp.IS_FRWD_CHAT:
        await db.defer_forwarding_task(task_id, delay_seconds=15)
        return
    temp.lock[owner_id] = True
    temp.forwardings += 1
    if destination not in temp.IS_FRWD_CHAT:
        temp.IS_FRWD_CHAT.append(destination)

    node_client = None
    batch_ids = []
    try:
        node_client = await start_clone_bot(IND_SYS_CLIENT.client(active_node))
        # Revalidate source access and destination write permission before replaying.
        await node_client.get_chat(source)
        await node_client.get_chat(destination)
        probe = await node_client.send_message(destination, "<i>Forwarding recovery permission check.</i>")
        await probe.delete()
        if limit <= cursor:
            logger.info("Task %s has no source IDs beyond checkpoint %s", task_id, cursor)
        else:
            await _notify(
                bot, owner_id,
                f"Resuming forwarding task {task_id} after source message ID {cursor}.",
            )

        # A crash could occur just after the outcome insert but before the cursor
        # update. Check only the first unconfirmed region until a fresh outcome is
        # reached; serial processing means there can be at most a small such gap.
        reconcile_cursor_gap = True
        async for msg in node_client.iter_messages(
            node_client,
            chat_id=source,
            limit=limit,
            offset=cursor,
        ):
            if msg is None:
                continue
            message_id = int(getattr(msg, "id", 0) or 0)
            if message_id <= cursor:
                continue

            if reconcile_cursor_gap:
                existing = await db.get_forwarding_message_outcome(task_id, message_id)
                if existing:
                    await db.checkpoint_forwarding_message(
                        task_id, message_id, existing["outcome"], existing.get("error")
                    )
                    cursor = message_id
                    state.add("fetched")
                    # Keep checking across empty/deleted ID placeholders; otherwise
                    # the first fresh placeholder could hide the pending outcome.
                    if not getattr(msg, "empty", False) and not getattr(msg, "service", False):
                        continue
                    continue

                is_empty = bool(getattr(msg, "empty", False))
                is_service = bool(getattr(msg, "service", False))
                if is_empty or is_service:
                    await db.checkpoint_forwarding_message(
                        task_id, message_id, "skipped", "empty_or_service"
                    )
                    state.add("fetched")
                    state.add("deleted")
                    cursor = message_id
                    continue
                reconcile_cursor_gap = False

            if getattr(msg, "empty", False) or getattr(msg, "service", False):
                # Pending earlier IDs must be settled before this later ID can
                # advance the monotonic checkpoint.
                if forward_tag and batch_ids:
                    await _flush_batch(node_client, batch_ids, task, state)
                    cursor = batch_ids[-1]
                    batch_ids = []
                await db.checkpoint_forwarding_message(
                    task_id, message_id, "skipped", "empty_or_service"
                )
                state.add("fetched")
                state.add("deleted")
                cursor = message_id
                continue

            state.add("fetched")
            if forward_tag:
                batch_ids.append(message_id)
                if len(batch_ids) >= RECOVERY_BATCH_SIZE:
                    await _flush_batch(node_client, batch_ids, task, state)
                    cursor = batch_ids[-1]
                    batch_ids = []
            else:
                details = {
                    "msg_id": message_id,
                    "media": extract_media_id(msg),
                    "caption": format_custom_caption(msg, caption_template),
                    "button": inline_button,
                    "protect": task.get("protect_content"),
                }
                copied = await execute_single_copy(node_client, details, None, state)
                await db.checkpoint_forwarding_message(
                    task_id,
                    message_id,
                    "forwarded" if copied else "failed",
                    None if copied else "copy failed after retries",
                )
                if copied:
                    state.add("total_files")
                cursor = message_id
                await asyncio.sleep(1 if task.get("active_node_is_bot") else 10)

        # Always flush the trailing partial batch, including when the source ends
        # exactly at the final message ID.
        if batch_ids:
            await _flush_batch(node_client, batch_ids, task, state)
            cursor = batch_ids[-1]
            batch_ids = []

        final_counts = await db.get_forwarding_outcome_counts(task_id)
        final_counts["processed"] = final_counts["forwarded"] + final_counts["skipped"] + final_counts["failed"]
        status = final_task_status(final_counts)
        await db.update_forwarding_task(task_id, {
            "counts": final_counts,
            "status": status,
            "completed_at": datetime.now(timezone.utc),
            "last_error": None,
        })
        await _notify(
            bot, owner_id,
            f"Forwarding task {task_id} finished with status: {status}.\n"
            f"Processed: {final_counts['processed']} | Forwarded: {final_counts['forwarded']} | "
            f"Skipped: {final_counts['skipped']} | Failed: {final_counts['failed']} | "
            f"Last confirmed source message ID: {cursor}.",
        )
        logger.info("Recovered task %s finished with %s", task_id, status)

    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("Recovery execution failed for task %s", task_id)
        raise
    finally:
        if batch_ids:
            # Batch contents without a confirmed outcome remain uncheckpointed.
            # A new worker can safely retry them after lease expiry.
            logger.warning("Task %s ended with %d unconfirmed batch IDs", task_id, len(batch_ids))
        if node_client is not None:
            try:
                await node_client.stop()
            except Exception:
                logger.warning("Could not stop recovered node for task %s", task_id, exc_info=True)
        if destination in temp.IS_FRWD_CHAT:
            temp.IS_FRWD_CHAT.remove(destination)
        temp.lock[owner_id] = False
        temp.forwardings = max(0, temp.forwardings - 1)
