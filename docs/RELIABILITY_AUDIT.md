# Reliability audit and recovery plan

Reviewed on 2026-10-14 against `main`; implementation status reflects the recovery branch.

## Findings

### Deployment
- The Dockerfile cloned `JishuDeveloper/Ultra-Forward-Bot` instead of running the source copied into the build context.
- The startup script cloned `indramegh123-rgb/Ultra-Forward-Bot`, then changed into a hard-coded directory that did not match the clone destination.
- `app.json` advertised a different repository.
- README documented `DATABASE_URI` / `DATABASE_NAME`; application configuration used `DB_URL` / `DB_NAME`.
- Required deployment configuration was not validated before connecting to Telegram and MongoDB.

### Forwarding durability
- `plugins/utils.py` stores session state in the process-local `ACTIVE_NETWORK_SESSIONS` dictionary.
- `plugins/regix.py` keeps progress counters, cancellation state, active destination locks, and batch queues in memory.
- The `notify` MongoDB collection records user IDs for restart notifications; it is not a forwarding task ledger.
- No durable cursor or per-source-message outcome record was found in the forwarding path.
- The batch queue's final flush depends on the remaining-count estimate and is not protected by a finalization block.
- Generic per-message copy exceptions are logged and counted as deleted, which loses the distinction between a permanent skip and a retryable failure.
- `/restart` reports success before replacing the process and does not persist active task progress.

## Deployment changes in this branch

- Container builds use the checked-out repository source and run the worker directly.
- Runtime startup no longer clones another repository.
- Heroku manifest repository and environment defaults align with this repository.
- Configuration accepts canonical `DB_URL` / `DB_NAME` and legacy `DATABASE_URI` / `DATABASE_NAME` aliases.
- Required settings fail fast with a clear missing-variable message.
- Heroku remains a single worker process; persistent MongoDB is required.

## Recovery design requirements

Recovery implementation in this branch persists:

- Stable task ID, owner, source chat, destination chat, source ID boundary, selected node reference, caption/button payload, and sanitized settings snapshot.
- Status, timestamps, worker lease, heartbeat, retry attempt count, and last confirmed source message ID.
- Per-message outcomes uniquely keyed by task ID and source message ID, plus aggregate processed/forwarded/skipped/failed counters.
- Atomic worker claims, lease renewal, startup recovery of interrupted/stale tasks, and `/fwdstatus` reporting.
- Separate `completed` and `completed_with_errors` terminal states.

### Delivery guarantee

Telegram send/copy and MongoDB cannot participate in one atomic transaction. If Telegram accepts a message and the process dies before recording the success in MongoDB, a restart may send that message again. The honest guarantee is at-least-once delivery with a small duplicate window unless destination-side reconciliation is implemented. Do not advertise exactly-once forwarding.

### Required tests before production use

1. Config aliases, missing variables, malformed owner IDs.
2. Task creation and unique message-outcome writes.
3. Cursor boundary tests, including empty sources and final partial batches.
4. Process restart between send and checkpoint.
5. Stale lease recovery and prevention of two workers claiming the same task.
6. FloodWait backoff and permanent-vs-retryable error classification.
7. Cancellation, finalization, and cleanup on exceptions.
8. Staging Telegram test with a small channel, followed by a controlled Heroku worker restart.

## Verification status

The branch includes automated CI checks for Python compilation, iterator checkpoint boundaries, resume-from-checkpoint behavior, terminal status classification, retry backoff, and `app.json` JSON parsing. Those tests do not replace a live Telegram/Heroku staging test with a controlled restart and real MongoDB lease contention. No live deployment or Telegram integration test is claimed as passed.

## Recovery behavior and remaining limitations

- The bot renews leases for active tasks and only reclaims tasks whose lease has expired or whose status is interrupted/recovering.
- Recovery reloads the originally selected node by owner and node ID, revalidates source/destination access, reconciles outcome counters from MongoDB, then resumes after the saved source message ID.
- Task outcomes are idempotently keyed by task ID + source message ID. A checkpoint repair handles the crash window between outcome insertion and task-counter/cursor update.
- A task with recorded delivery failures ends as `completed_with_errors`. `/fwdstatus` reports the latest task and up to 10 failed source IDs.
- Per-message unexpected errors are retried up to three times; worker-level recovery failures use bounded exponential delay and stop after five attempts, setting `needs_attention`.

Telegram delivery and MongoDB checkpoint writes cannot be one atomic operation. The guarantee remains at-least-once: a crash between an accepted Telegram send and its checkpoint can duplicate a single copy-mode message, or an uncheckpointed native-forward batch of up to 50 source IDs. If the stored node has been removed, the task requires operator attention rather than switching credentials.

Before production rollout, run a staging test with a small channel and persistent MongoDB, then restart the Heroku worker during copy mode and native-forward mode. Also verify lease contention across two worker instances and inspect `/fwdstatus` after recovery.
