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

        # Ensure durable recovery collections/indexes exist before accepting work.
        await db.ensure_forwarding_indexes()
        interrupted = await db.mark_interrupted_forwarding_tasks()
        if interrupted:
            logging.warning(
                "%s forwarding task(s) were interrupted. Their durable checkpoints "
                "are retained; automatic replay is intentionally not attempted until "
                "the task's original node/session and options can be revalidated.",
                interrupted,
            )
            tasks = await db.forwarding_tasks.find({"status": "interrupted"}).to_list(length=500)
            for task in tasks:
                try:
                    await self.send_message(
                        int(task["owner_id"]),
                        "⚠️ A forwarding task was interrupted by a worker restart. "
                        f"Task ID: {task['task_id']} | Last checkpoint: "
                        f"{task.get('cursor_message_id', 0)}. "
                        "The checkpoint is saved, but this version does not auto-replay "
                        "the task because Telegram may have accepted a message immediately "
                        "before the crash. Please review the destination before retrying.",
                    )
                except Exception as notify_error:
                    logging.warning("Could not notify owner for interrupted task %s: %s",
                                     task.get("task_id"), notify_error)

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

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        logging.info(msg)









# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper