# Ultra-Forward-Bot — End-to-End User Guide

This guide explains how to configure and use Ultra-Forward-Bot from a fresh start. You do not need to understand the code or Heroku to use the Telegram commands.

## 1. Understand the two accounts

There are two separate roles:

1. **Controller bot** — the Telegram bot deployed on Heroku. You chat with this bot to use commands such as `/start`, `/settings`, and `/forward`.
2. **Connected node** — a separate Telegram bot token or a Telegram user session that you attach through `/settings`. The node is the account the forwarding engine uses to access the source and post messages to the destination.

The controller bot is **not automatically the forwarding node**. You must attach a node and give it access to the chats you intend to use.

The safest way to learn the workflow is to start with a small test channel and a destination where you can inspect the results.

## 2. The recommended first-time setup

Follow these steps in order:

1. Open your controller bot in Telegram and send `/start`.
2. Send `/settings`.
3. Attach one connected node.
4. Register a destination under **Target Zones**.
5. Confirm that the node can read the source and post to the destination.
6. Run a small test with `/forward`.
7. Check the result with `/fwdstatus`.

Do not start with hundreds of thousands of messages. Confirm the source, destination, output format, and permissions with a small range first.

## 3. Attach a connected node

Send `/settings` and tap **Connected Nodes**.

The menu offers a choice between attaching a bot and attaching a userbot when no node is registered. The current interface stores one connected node per user at a time.

### Option A — Attach a bot

Use this if you want a dedicated bot account to do the forwarding.

1. Create a separate bot with [@BotFather](https://t.me/BotFather), or use a bot you already control.
2. In the controller bot's **Connected Nodes** menu, choose **Attach Bot**.
3. Follow the prompt and **forward the original BotFather message containing the new bot token** to the controller bot. The current implementation validates that the token message was forwarded from BotFather; simply typing the token may be rejected even though the prompt mentions pasting.
4. Wait for the success message.

Then add that connected bot to the source chat with enough access to read the messages you want to process. In a destination channel, make it an administrator with permission to post messages. In a group, check that its posting permissions are sufficient.

### Option B — Attach a userbot

Use this if the forwarding account needs access that your bot account does not have and you understand the security risks.

1. Open `/settings` → **Connected Nodes** → **Attach Userbot**.
2. Submit a valid Pyrogram V2 session string when prompted.
3. Wait for the verification and success message.
4. Make sure that user account is a member of the source and can post in the destination.

**Security warning:** a user session string can give access to the Telegram account and its chats. Treat it like a password. Only use a session you control, do not share it, and only provide it to a deployment you trust. The project itself warns that using a userbot can carry Telegram account-ban risk. Never put a bot token or user session in a public issue, screenshot, or repository.

### Changing the connected node

If a node is already attached, the Connected Nodes menu shows the registered node and lets you inspect or remove it. To use a different node, remove the current one and attach the replacement. Before removing a node, remember that an interrupted task may need its original node to recover.

## 4. Register a destination under Target Zones

A **Target Zone** is a destination chat or channel where messages will be posted.

1. Send `/settings`.
2. Tap **Target Zones**.
3. Tap **Add New Zone**.
4. In Telegram, forward a message **from the destination channel or chat** to the controller bot.
5. Wait for the registration confirmation.

Repeat this for any additional destinations. When you later run `/forward`, the bot automatically uses the only registered destination, or asks you to select one if you have registered several.

The destination must allow the **connected node** to post. For a channel, give the node the right administrator permissions. Registering a destination with the controller bot does not automatically give the connected node access to it.

## 5. Give the node source access

The **source** is the channel or chat you want to read messages from.

Before starting a task, ensure the connected node can access that source. For a private source, the node must be an authorized member. If the source or destination is inaccessible, the bot may stop during its connection checks.

You can use a public message link or a private channel message link, provided the connected node is allowed to access it. The source link must identify a specific message, not just the channel home page.

Examples of accepted link shapes:

- Public channel: `https://t.me/channelusername/120`
- Private channel: `https://t.me/c/1234567890/120`

Replace the example channel and message IDs with your real values. The private-link format works only if the connected node already has access to that private channel.

## 6. Run your first forwarding task

Send `/forward`. The shorter alias `/fwd` also starts the same workflow.

The bot will guide you through these prompts.

### Step 1 — Choose the destination

If you registered multiple Target Zones, select the destination from the keyboard. If you registered only one, the bot selects it automatically.

### Step 2 — Identify the source

When prompted, either:

- **Send a link to a specific message** in the source channel; or
- Forward a message from the source channel to the controller bot when Telegram preserves the channel as the message's origin.

A full message link is usually clearer. Do not send only `@channelusername` or the channel homepage URL.

**Important:** the link identifies the *upper boundary* for this task. The current interface does not ask you for an arbitrary starting message ID. The forwarding loop scans source message IDs from the beginning up through the message ID in the link, subject to the skip value and any messages that cannot be retrieved. For example, a link ending in `/120` sets the endpoint at message ID 120. A link ending in `/800000` can result in a very large task.

### Step 3 — Enter the skip value

The bot asks how many initial message positions to skip.

- Enter `0` to start at the beginning of the source's message-ID sequence.
- Enter `5` to bypass the first five message-ID positions and start after them.

Use a non-negative whole number. If you are unsure, enter `0` for a small test.

Telegram channels can contain gaps in message IDs because messages may have been deleted or otherwise be unavailable. Therefore, the skip value is best understood as a message-ID offset, not a guarantee that exactly that many visible posts will be skipped.

### Step 4 — Review the confirmation

The bot displays the selected node, source, destination, and skip value. Check these carefully before proceeding.

- Tap **Yes, Ignite Engine** to start.
- Tap **Abort** to cancel before the task starts.

### Step 5 — Watch the live task

A status message shows progress information and provides a button to open the live status popup. While a task is running, its status message also has an abort button.

To stop a running task, tap **Abort Operation** in the task's status controls. During an interactive setup prompt, send `/cancel` when the prompt says it can be cancelled.

## 7. Choose how messages should be delivered

The **Forward Tag** option is in `/settings` → **Filter Engine**.

- **Forward Tag ON:** the engine uses Telegram's native forward operation. Messages retain Telegram's forwarded-message attribution where Telegram allows it.
- **Forward Tag OFF:** the engine uses copy mode. This avoids the usual forwarded-message attribution and is the mode to use when you want the configured custom caption and inline buttons applied.

For your first test, keep the default settings unless you have a specific reason to change them. If you want a custom caption or buttons, use copy mode and test the result with one or two messages first.

## 8. Configure captions and inline buttons (optional)

These options are not required for basic forwarding. Set them only after you have completed a successful test using the default configuration.

### Custom caption

1. Send `/settings`.
2. Choose **Caption Inject**.
3. Choose to add or modify the caption.
4. Use any of these placeholders in your caption template:

| Placeholder | Meaning |
|---|---|
| `{filename}` | File name from the source media message, where available |
| `{size}` | Human-readable file size, where available |
| `{caption}` | Original caption, where available |

Example template:

```text
File: {filename}
Size: {size}

{caption}
```

Use **View Caption** to inspect your saved template, or **Wipe Caption** to remove it. Caption placeholders apply to supported media messages; do not assume every plain-text post has a file name or size.

### Inline buttons

1. Send `/settings`.
2. Choose **Inline Buttons**.
3. Choose **Inject Button**.
4. Enter button markup in this format:

```text
[Button label][buttonurl:https://example.com]
```

For example:

```text
[Open website][buttonurl:https://example.com]
```

Replace the example URL with a destination you control or trust. Use the view option to inspect the saved buttons, or wipe the saved button configuration to remove them. Test this in copy mode before using a custom caption/button layout for a large task.

## 9. Understand the other settings

The settings menu contains several advanced options. They can affect which messages are copied or how the output behaves, so change them one at a time.

| Setting | What it is intended to control | First-time advice |
|---|---|---|
| **Filter Engine** | Forward Tag and message-type toggles such as text, documents, videos, photos, audio, voice notes, animations, stickers, polls, and duplicate handling | Leave defaults for the first test. Treat filtering and duplicate options as experimental until you verify the exact result in a test destination. |
| **Advanced Parameters** | Content protection, size-limit settings, blocked extensions, and allowed keywords | Leave unchanged until basic forwarding works. Do not rely on these options as guaranteed safeguards without testing them. |
| **Database Link** | An optional MongoDB connection used by advanced duplicate-check functionality | Leave blank for normal forwarding unless you specifically understand and need that feature. It is separate from the MongoDB URI used to run the deployed controller bot. |
| **Target Zones** | Stores the destination chats you can select when starting a task | Register every destination once. |
| **Connected Nodes** | The bot or user account that reads and posts messages | Confirm it has access to both ends of the transfer. |

**Important implementation note:** the current code exposes filter, size, extension, keyword, and duplicate controls in the interface, but the forwarding loop does not consistently enforce every one of those options across all paths. Do not rely on them to guarantee that a particular file type or keyword will be excluded. Test any advanced option on a small task and inspect the destination before using it for critical or large-scale forwarding.

## 10. Check progress with `/fwdstatus`

Send:

```text
/fwdstatus
```

The command shows the latest task recorded for your Telegram account, including:

- Task status, source, and destination
- Processed, forwarded, skipped, and failed counts
- Last confirmed source message ID
- Up to 10 known failed source message IDs

The most useful statuses are:

| Status | Meaning |
|---|---|
| `running` | The task is active or has been claimed for recovery. |
| `completed` | The recorded task finished without known delivery failures. |
| `completed_with_errors` | The task reached the end but one or more delivery errors were recorded. |
| `interrupted` / `recovering` | The worker is retrying or waiting to resume a task. |
| `needs_attention` | The recovery worker could not safely continue, for example because the original node is no longer registered or available. |

Use `/fwdstatus` after a worker restart to inspect the latest checkpoint. If the task says `needs_attention`, check the source, destination, and original connected node before starting a new forwarding run.

**Do not confuse `/status` and `/fwdstatus`:** the owner-only `/status` command reports system statistics; `/fwdstatus` reports your latest forwarding task.

## 11. What happens if Heroku restarts?

The worker stores task progress and individual outcomes in MongoDB so a process restart does not automatically erase the saved progress. A background recovery worker can claim an interrupted task after the previous worker's lease expires, validate the original node, and try to continue after the saved message ID.

There is one important limitation: **delivery is at least once, not exactly once**. Telegram cannot combine sending a message and saving the MongoDB checkpoint into a single atomic operation. If Heroku stops the worker after Telegram accepted a message but before the checkpoint is saved, that message can be delivered again during recovery. In native-forward mode, an uncheckpointed batch of up to 50 message IDs can be replayed.

Previously checkpointed batches are not intentionally restarted, but no user should treat this as a guarantee that duplicates are impossible. Keep the same persistent MongoDB database across deploys and restarts.

For very large channels, run a controlled test first. Do not start a new copy of a huge task merely because the old task's status briefly shows as interrupted; check `/fwdstatus` and let recovery have a chance to work.

## 12. Common problems

| Problem | What to check |
|---|---|
| **“Node not found”** | Open `/settings` → **Connected Nodes** and attach a bot or userbot. |
| **“Target zone missing”** | Open `/settings` → **Target Zones** → **Add New Zone**, then forward a message from the intended destination chat to the controller. |
| **Source link rejected** | Send a full message link ending in a message ID, not only a channel username or homepage link. |
| **Source access denied** | Confirm the selected node is a member of the source and can access its messages, especially for private channels. |
| **Destination write access denied** | Give the selected node permission to post in the destination. For channels, check its administrator permissions. |
| **Forwarding started in the wrong destination** | Stop the task and verify your registered Target Zones in `/settings` before starting again. |
| **The task finished with delivery errors** | Use `/fwdstatus` and inspect the failed source message IDs. Check permissions and whether those messages can be accessed and copied. |
| **Task says `needs_attention` after a restart** | Check whether the original connected node is still registered and still has access to both chats. Do not silently replace its credentials while expecting the old task to resume. |
| **Bot is online but doesn't respond** | Send `/ping`. If it still does not respond, inspect the Heroku worker logs and confirm the worker is running. |

## 13. Other commands

| Command | Purpose |
|---|---|
| `/start` | Open the start menu and the Help/About buttons. |
| `/settings` | Open node, destination, caption, button, and advanced settings. |
| `/forward` or `/fwd` | Start the forwarding setup. |
| `/fwdstatus` | Show the latest task's saved progress and failures. |
| `/ping` | Check whether the controller bot is responding. |
| `/cancel` | Cancel an interactive setup prompt when supported. Use the task's abort button for a running transfer. |
| `/reset` | Restore your settings to defaults. This can remove your custom preferences, so do not use it as a routine fix. |
| `/unequify` | Scan a destination for duplicate documents and delete duplicates. This is destructive; review the target carefully and use it only if you understand the operation. |
| `/status` | Owner-only system statistics. |
| `/restart` | Owner-only worker restart. Avoid restarting manually during an active task unless necessary. |

Owner-only administrative commands are intended for the deployment owner, not routine forwarding.

## 14. A safe first-run checklist

Before pressing **Yes, Ignite Engine**, check each item:

- [ ] I attached the correct connected node.
- [ ] The node can access the source chat.
- [ ] I registered the intended destination under Target Zones.
- [ ] The node can post to the destination.
- [ ] The source input identifies the correct final message.
- [ ] I understand that the bot scans from the start of the message-ID sequence to the selected endpoint.
- [ ] I entered the correct skip value.
- [ ] I have left advanced filters alone or tested any changes separately.
- [ ] I am using a small test first and have checked the destination output.

Once the test looks correct, repeat the same steps with the intended source endpoint. For large tasks, keep `/fwdstatus` handy and verify the destination after completion or recovery.

## 15. Permissions and responsible use

Only forward content that you own or are permitted to redistribute. Follow Telegram's terms and the rules of the source and destination communities. Do not use a connected bot or user session to access chats without authorization, and protect all tokens, session strings, and database credentials.
