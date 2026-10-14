# Reliability audit and recovery plan

Reviewed on 2026-10-14 against `main`.

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

A correct implementation must persist, at minimum:

- Stable task ID, owner, source chat, destination chat, source range, and all forwarding options.
- Status (`queued`, `running`, `paused`, `completed`, `cancelled`, `failed`), created/updated timestamps, lease/heartbeat, and attempt count.
- A durable cursor and counts for forwarded, skipped, filtered, duplicate, and failed messages.
- Per-message outcomes keyed uniquely by task ID and source message ID, with failure class and retry count.
- Atomic cursor/outcome updates and a startup recovery routine that reclaims only stale leases.

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

Repository inspection and branch edits are complete for the deployment/configuration stage. A live Heroku build, live Telegram forwarding test, and production recovery test require the owner's deployment environment and credentials; they are not claimed as passed here. Do not enable unattended auto-resume of large jobs until the recovery tests above pass.


## Implementation status after recovery-stage changes

The current branch now includes:
- A dedicated MongoDB `forwarding_tasks` collection and `forwarding_message_outcomes` ledger.
- Unique task/message indexes and idempotent outcome inserts.
- Checkpoint writes for individual-copy outcomes and batch outcomes.
- An explicit final partial-batch flush.
- Startup detection of tasks left in `running` / `recovering` and owner notification while retaining checkpoints.

**Important remaining gap:** automatic re-execution from the saved checkpoint is not yet enabled. The task envelope does not yet persist every runtime dependency (notably a validated, recoverable node credential reference and all filter/duplicate-check settings), and replaying from a cursor without reconciling destination messages can duplicate content. Startup therefore surfaces interrupted tasks instead of silently replaying them. This is safer than losing task records, but it does not satisfy unattended automatic recovery yet.

The next implementation stage must persist the complete sanitized execution plan, restore/revalidate the chosen node, implement a lease-based resume worker that reuses the same forwarding engine, and add crash-window tests. Do not describe this branch as providing automatic resume until that stage is complete.
