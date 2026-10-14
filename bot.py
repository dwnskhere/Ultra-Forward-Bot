# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper




import asyncio
import logging 
import logging.config
from database import db 
from config import Config  
from pyrogram import Client, __version__
from pyrogram.raw.all import layer 
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait 

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client): 
    def __init__(self):
        super().__init__(
            Config.BOT_SESSION,
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins={
                "root": "plugins"
            },
            workers=50,
            bot_token=Config.BOT_TOKEN
        )
        self.log = logging

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"{me.first_name} with for pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        self.id = me.id
        self.username = me.username
        self.first_name = me.first_name
        self.set_parse_mode(ParseMode.DEFAULT)
        text = "**Bot Restarted !**"
        logging.info(text)

        # Create indexes and start lease/heartbeat-based task recovery.
        await db.ensure_forwarding_indexes()
        stale_count = await db.mark_interrupted_forwarding_tasks()
        if stale_count:
            logging.warning("Marked %s forwarding task(s) with expired leases for recovery.", stale_count)
        self._forwarding_recovery_task = asyncio.create_task(
            self._forwarding_recovery_loop(), name="forwarding-recovery-worker"
        )

        success = failed = 0
        users = await db.get_all_frwd()
        async for user in users:
           chat_id = user['user_id']
           try:
              await self.send_message(chat_id, text)
              success += 1
           except FloodWait as e:
              await asyncio.sleep(e.value + 1)
              await self.send_message(chat_id, text)
              success += 1
           except Exception:
              failed += 1 
    #    await self.send_message("venombotsupport", text)
        if (success + failed) != 0:
           await db.rmve_frwd(all=True)
           logging.info(f"Restart message status"
                 f"success: {success}"
                 f"failed: {failed}")

    async def _forwarding_recovery_loop(self):
        """Renew live leases and resume abandoned tasks one at a time."""
        while True:
            try:
                await db.heartbeat_owned_tasks()
                await db.mark_interrupted_forwarding_tasks()
                task = await db.claim_next_recoverable_task()
                if task:
                    from datetime import datetime, timedelta, timezone
                    from plugins.recovery import recover_forwarding_task, retry_delay_seconds

                    task_id = str(task["task_id"])
                    attempt = int(task.get("attempt", 1))
                    try:
                        await recover_forwarding_task(self, task)
                    except asyncio.CancelledError:
                        raise
                    except Exception as recovery_error:
                        error_text = str(recovery_error)[:1000]
                        if attempt >= 5:
                            await db.update_forwarding_task(task_id, {
                                "status": "needs_attention",
                                "last_error": error_text,
                                "recovery_note": "Automatic recovery stopped after five failed attempts.",
                            })
                            try:
                                await self.send_message(
                                    int(task["owner_id"]),
                                    f"Forwarding task {task_id} could not be recovered after five attempts. "
                                    f"Last error: {error_text}",
                                )
                            except Exception:
                                logging.warning("Could not notify owner about task %s", task_id)
                        else:
                            retry_after = datetime.now(timezone.utc) + timedelta(
                                seconds=retry_delay_seconds(attempt)
                            )
                            await db.update_forwarding_task(task_id, {
                                "status": "interrupted",
                                "last_error": error_text,
                                "retry_after": retry_after,
                            })
                            logging.warning(
                                "Task %s recovery attempt %s failed; retrying after %s: %s",
                                task_id, attempt, retry_after.isoformat(), error_text,
                            )
                    continue
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.exception("Forwarding recovery worker iteration failed")
            await asyncio.sleep(15)

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        recovery_task = getattr(self, "_forwarding_recovery_task", None)
        if recovery_task and not recovery_task.done():
            recovery_task.cancel()
            try:
                await recovery_task
            except asyncio.CancelledError:
                pass
        await super().stop()
        logging.info(msg)









# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper