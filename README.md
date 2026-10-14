# Ultra-Forward-Bot

A Telegram channel and chat forwarding bot built with [Pyrofork](https://github.com/KurimuzonAkuma/pyrogram) and MongoDB. It runs as a background **worker**—there is no web dashboard.

<p align="center">
  <a href="https://www.heroku.com/deploy?template=https://github.com/dwnskhere/Ultra-Forward-Bot">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku">
  </a>
</p>

> **Before deploying:** provide your own Telegram credentials and a reachable, persistent MongoDB database. Heroku charges for the worker dyno and any other resources used. Heroku Deploy Buttons are not available for the Fir generation; see the [official Heroku Button guide](https://devcenter.heroku.com/articles/heroku-button).

## Features

- Forward messages between Telegram channels and chats using a registered bot or user session.
- Choose native forwarding or copy-based forwarding; copy mode supports custom captions and inline buttons.
- Save task checkpoints and message outcomes in MongoDB so progress survives a worker restart.
- Automatically attempt recovery from the saved checkpoint using worker leases and heartbeats.
- Track successful, skipped, and failed messages separately.
- Review the latest task with `/fwdstatus`, including the last confirmed source message ID and up to 10 known failed message IDs.
- Configure forwarding behavior through the bot's settings interface.

## Deploy to Heroku

### One-click deployment

1. Click **Deploy to Heroku** above and sign in to Heroku.
2. Choose an app name and fill in the required config variables listed below.
3. Confirm the deployment and review the plan and billing information before creating the app.
4. After deployment, open the app's **Resources** tab and verify that one `worker` dyno is running.
5. Open your Telegram bot and send `/start`.

This is a worker application, so it does not serve a website. Use Telegram to operate it and Heroku logs to troubleshoot the runtime.

### Required configuration

| Variable | Required | Description |
|---|---|---|
| `API_ID` | Yes | Telegram API ID from [my.telegram.org](https://my.telegram.org). |
| `API_HASH` | Yes | Telegram API hash from [my.telegram.org](https://my.telegram.org). |
| `BOT_TOKEN` | Yes | Token for your bot from [@BotFather](https://t.me/BotFather). |
| `OWNER_ID` | Yes | Telegram user ID(s) allowed to run owner-only commands. Separate multiple IDs with spaces. |
| `DB_URL` | Yes | Connection URI for a persistent MongoDB database, such as MongoDB Atlas. |
| `DB_NAME` | No | MongoDB database name. Defaults to `IND_BOTZ_FORWARD`. |
| `BOT_SESSION` | No | Pyrogram session name. Defaults to `Indra-forward-bot`. |

The legacy variables `DATABASE_URI` and `DATABASE_NAME` are also accepted as aliases for `DB_URL` and `DB_NAME`. New deployments should use the canonical names.

**MongoDB is not provisioned by the Heroku button.** Create or select a persistent MongoDB database and put its connection URI in `DB_URL`. Ensure the database network access rules allow connections from your deployment environment. Do not use localhost, and do not commit database URIs, bot tokens, API credentials, or user-session strings to Git.

### Runtime and deployment configuration

The repository uses `heroku.yml` and `Dockerfile` to build the container. The app manifest sets Heroku's `container` stack and requests one `worker` dyno. This is intentional: running more than one worker can increase concurrency and should only be done after validating lease behavior and resource usage.

For deployments outside the Deploy Button flow, follow Heroku's [Docker deployment guide](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml). The worker command is:

```sh
python main.py
```

## Telegram commands

| Command | Purpose |
|---|---|
| `/start` | Open the bot's start menu. |
| `/forward` | Configure and start a forwarding task. |
| `/fwdstatus` | Show the latest task's status, counters, checkpoint, and known failed message IDs. |
| `/settings` | Configure forwarding preferences and the bot/user session. |
| `/unequify` | Scan a destination for duplicate documents. |
| `/cancel` | Cancel the current interactive operation or active task where supported. |
| `/reset` | Restore the user's settings to defaults. |
| `/restart` | Restart the worker (owner only). |
| `/resetall` | Reset all user settings (owner only). |

The selected Telegram node must have access to the source chat and permission to write to the destination. For private chats or channels, ensure the correct bot or user session is a member and has the required access.

## Progress recovery and delivery guarantees

MongoDB stores the task ID, source and destination, selected node reference, task status, timestamps, counters, last confirmed source message ID, and per-message outcomes. A background recovery worker claims interrupted or stale tasks with a lease, refreshes its heartbeat, validates the stored node, and attempts to resume source iteration after the saved checkpoint.

Use `/fwdstatus` after a restart to inspect the latest saved progress. If the original node is no longer available, the task may move to `needs_attention` instead of silently switching to different credentials.

**Delivery is at least once, not exactly once.** Telegram cannot atomically combine a send/copy operation with a MongoDB checkpoint. If the worker stops after Telegram accepts a message but before the checkpoint is saved, a message may be delivered again during recovery. In native-forward mode, an uncheckpointed batch of up to 50 source IDs may be replayed. Previously checkpointed batches are not intentionally restarted.

Heroku's filesystem and process memory are not durable storage. Keep using the same persistent MongoDB database across deploys and restarts. Before running a very large forwarding job, test recovery with a small source chat and confirm that `/fwdstatus` shows the expected results.

## Development and tests

Python 3.10 is used by the container.

Install the project dependencies and run the checks:

```sh
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
```

GitHub Actions runs the compilation and regression tests on pushes and pull requests. These automated checks cover the source-iterator boundary, resume offset, recovery status helpers, retry backoff, and Heroku manifest JSON/configuration. They do **not** replace a live Telegram/Heroku staging test with a controlled restart.

## Troubleshooting

- **The bot exits at startup:** Check that every required config variable is set correctly, especially `API_ID`, `API_HASH`, `BOT_TOKEN`, `OWNER_ID`, and `DB_URL`.
- **MongoDB authentication or connection errors:** Recheck the URI, database user's permissions, and network access rules.
- **The worker is not running:** In Heroku, open **Resources** and verify that `worker` is scaled to one dyno; then inspect the app logs.
- **A task needs attention after restart:** Check `/fwdstatus`, restore access for the originally selected Telegram node, and review the source and destination before manually retrying.

