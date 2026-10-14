# Ultra-Forward-Bot

Telegram forwarding bot built with Pyrofork and MongoDB.

## Required environment variables

- `BOT_TOKEN` — Telegram bot token from [@BotFather](https://t.me/BotFather).
- `API_ID` and `API_HASH` — Telegram application credentials from [my.telegram.org](https://my.telegram.org).
- `OWNER_ID` — one or more owner Telegram user IDs, separated by spaces.
- `DB_URL` — persistent MongoDB connection URI. The legacy alias `DATABASE_URI` is also accepted.
- `DB_NAME` — MongoDB database name. The legacy alias `DATABASE_NAME` is also accepted; defaults to `IND_BOTZ_FORWARD`.
- `BOT_SESSION` — optional Pyrogram session name.

Set credentials through your hosting provider's environment/configuration settings. Do not commit credentials or session strings.

## Features

- Forward messages from public and private channels to a destination.
- Broadcast support.
- Custom captions and inline buttons.
- Restricted-chat support where the connected bot/user session has access.
- Duplicate skipping.
- Message-type, extension, keyword, and size filters.
- Settings stored in MongoDB.

## Commands

- `/start` — start the bot.
- `/forward` — configure and start forwarding.
- `/fwdstatus` — inspect the latest forwarding task, checkpoint, successful count, and up to 10 failed source message IDs.
- `/unequify` — scan a channel for duplicate messages.
- `/settings` — configure forwarding.
- `/ping` — check bot responsiveness.
- `/cancel` — cancel an active operation.
- `/reset` — reset your settings.
- `/stats` — owner-only statistics.
- `/resetall` — owner-only settings reset.
- `/broadcast` — owner-only broadcast.
- `/restart` — owner-only process restart.

## Heroku / container deployment

This application is a **worker**, not a web application. The Procfile runs `python3 main.py`; the container image runs the checked-out source directly and does not clone a second repository at runtime.

Configure the same persistent MongoDB URI across deploys. Heroku's filesystem and process memory are ephemeral, so forwarding progress and per-message outcomes are stored in MongoDB. The recovery worker uses a worker lease and heartbeat, waits for an expired lease, then resumes source iteration strictly after the last confirmed source message ID.

A task ends as `completed` when all recorded outcomes succeeded or were skipped, and as `completed_with_errors` when delivery failures were recorded. Use `/fwdstatus` to review progress and up to 10 failed source IDs. If the originally selected bot/user session is no longer registered, the task moves to `needs_attention` rather than silently switching credentials.

Delivery is **at least once, not exactly once**. Telegram cannot atomically commit a send and the MongoDB checkpoint together, so a crash after Telegram accepts a message but before MongoDB records it can duplicate that message. For native-forward mode, an uncheckpointed batch of up to 50 source IDs can be replayed; already checkpointed batches are not intentionally replayed.

## Development checks

Run syntax compilation and regression tests with:

```sh
python -m compileall -q .
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on pushes and pull requests. The automated tests cover the iterator boundary/resume offset, status classification, retry backoff, and `app.json` parsing. A live Telegram/Heroku staging test—including a controlled restart during a small forwarding task—is still required before production rollout.
