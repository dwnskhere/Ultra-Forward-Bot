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

Configure the same persistent MongoDB URI across deploys. Heroku's filesystem and process memory are ephemeral, so in-memory state is not a recovery mechanism. Until durable task checkpoints are implemented and verified, do not treat an interrupted large forwarding job as automatically resumable.

## Development checks

Run syntax compilation with:

```sh
python -m compileall -q .
```

Automated forwarding/recovery tests and a live Telegram/Heroku deployment test are still required before claiming production-safe restart recovery.
