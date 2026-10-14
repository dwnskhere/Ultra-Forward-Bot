# █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
# █ 🛡️ ꜱʏꜱᴛᴇᴍ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ & ᴜɪ ᴄᴏʀᴇ ᴠ3.0 [ᴇɴᴛᴇʀᴘʀɪꜱᴇ ᴇᴅɪᴛɪᴏɴ]
# █ 🎯 ᴏᴡɴᴇᴅ & ᴏᴘᴇʀᴀᴛᴇᴅ ʙʏ @IND_BOTZ 
# █ ⚠️ ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ - ᴘʀɪᴠᴀᴛᴇ ɴᴇᴛᴡᴏʀᴋ ᴄᴏʀᴇ
# █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

import os
import sys
import asyncio 
from html import escape
import logging
from database import db, mongodb_version
from config import Config, temp
from platform import python_version
from translation import Translation
from pyrogram import Client, filters, enums, __version__ as pyrogram_version
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument

# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ɢʟᴏʙᴀʟ ꜱʏꜱᴛᴇᴍ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ & ʟᴏɢɢɪɴɢ ᴘʀᴏᴛᴏᴄᴏʟꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [IND_START_CORE] - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
start_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🎨 ɢʟᴏʙᴀʟ ᴜɪ ᴍᴀᴛʀɪx (ᴍᴀɪɴ ᴍᴇɴᴜ ʙᴜᴛᴛᴏɴꜱ)
# ------------------------------------------------------------------------------------------------------------------------------------------------

SYSTEM_MAIN_BUTTONS = [
    [
        InlineKeyboardButton('📢 ᴏꜰꜰɪᴄɪᴀʟ ᴜᴘᴅᴀᴛᴇꜱ', url='https://t.me/IND_BOTZ'),
        InlineKeyboardButton('💬 ɴᴇᴛᴡᴏʀᴋ ꜱᴜᴘᴘᴏʀᴛ', url='https://t.me/IND_BOTZ')
    ],[
        InlineKeyboardButton('🛠️ ꜱʏꜱᴛᴇᴍ ʜᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('🤖 ᴀʙᴏᴜᴛ ᴇɴɢɪɴᴇ', callback_data='about')
    ],[
        InlineKeyboardButton('🧑‍💻 ᴄᴏʀᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑‍💻', url='https://t.me/IND_BOTZ')
    ]
]

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🚀 ᴍᴀɪɴ ᴇxᴇᴄᴜᴛɪᴏɴ ʙʟᴏᴄᴋ: ꜱᴛᴀʀᴛ ᴘʀᴏᴛᴏᴄᴏʟ
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_message(filters.private & filters.command(['start']))
async def initialize_start_sequence(client_bot, message_obj):
    """
    Core Entry Point for users.
    Registers new clients to the database and deploys the welcome interface.
    """
    client_info = message_obj.from_user
    
    # Database Registration Check
    if not await db.is_user_exist(client_info.id):
        await db.add_user(client_info.id, client_info.first_name)
        start_logger.info(f"New client registered to network: {client_info.id} ({client_info.first_name})")
        
    layout_markup = InlineKeyboardMarkup(SYSTEM_MAIN_BUTTONS)
    
    # Premium Welcome Animation (Sticker)
    try:
        welcome_sticker = await message_obj.reply_sticker("CAACAgUAAxkBAAECEEBlLA-nYcsWmsNWgE8-xqIkriCWAgACJwEAAsiUZBTiPWKAkUSmmh4E")
        await asyncio.sleep(2)
        await welcome_sticker.delete()
    except Exception as e:
        start_logger.warning(f"Failed to send welcome sticker: {e}")
        pass
        
    formatted_text = Translation.START_TXT.format(client_info.mention)
    
    await message_obj.reply_text(
        text=formatted_text,
        reply_markup=layout_markup,
        quote=True
    )

@Client.on_message(filters.private & filters.command(["fwdstatus"]))
async def latest_forwarding_status(client_bot, message_obj):
    """Show the caller's most recent durable forwarding task and known failures."""
    if not message_obj.from_user:
        return
    task = await db.get_latest_forwarding_task(message_obj.from_user.id)
    if not task:
        return await message_obj.reply_text(
            "No forwarding task has been recorded for your account yet."
        )

    counts = task.get("counts") or {}
    forwarded = int(counts.get("forwarded", 0))
    skipped = int(counts.get("skipped", 0))
    failed = int(counts.get("failed", 0))
    processed = int(counts.get("processed", forwarded + skipped + failed))
    cursor = task.get("last_confirmed_message_id", task.get("cursor_message_id", 0))
    failure_ids = await db.get_failed_message_ids(task["task_id"], limit=10)
    failure_text = ", ".join(str(item) for item in failure_ids) if failure_ids else "None recorded"
    status = escape(str(task.get("status", "unknown")).replace("_", " "))
    source = escape(str(task.get("source_chat_id", "Unknown")))
    destination = escape(str(task.get("destination_chat_id", "Unknown")))
    task_id = escape(str(task.get("task_id", "Unknown")))
    started = task.get("created_at")
    started_text = escape(started.strftime("%Y-%m-%d %H:%M UTC")) if hasattr(started, "strftime") else "Unknown"

    report = (
        "<b>Latest Forwarding Task</b>\n\n"
        f"<b>Task ID:</b> <code>{task_id}</code>\n"
        f"<b>Status:</b> <code>{status}</code>\n"
        f"<b>Source:</b> <code>{source}</code>\n"
        f"<b>Destination:</b> <code>{destination}</code>\n"
        f"<b>Started:</b> <code>{started_text}</code>\n\n"
        f"<b>Processed:</b> <code>{processed}</code>\n"
        f"<b>Successfully forwarded:</b> <code>{forwarded}</code>\n"
        f"<b>Skipped:</b> <code>{skipped}</code>\n"
        f"<b>Failed:</b> <code>{failed}</code>\n"
        f"<b>Last confirmed source message ID:</b> <code>{cursor}</code>\n\n"
        f"<b>Known failed source message IDs (max 10):</b>\n<code>{escape(failure_text)}</code>"
    )
    await message_obj.reply_text(
        report,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🔄 ꜱʏꜱᴛᴇᴍ ʀᴇʙᴏᴏᴛ ᴘʀᴏᴛᴏᴄᴏʟ [ᴀᴅᴍɪɴ ᴏɴʟʏ]
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_message(filters.private & filters.command(['restart', "r"]) & filters.user(Config.OWNER_ID))
async def trigger_system_reboot(client_bot, message_obj):
    """
    Safely shuts down current processes and restarts the Python execution environment.
    """
    start_logger.info(f"System reboot triggered by Admin {message_obj.from_user.id}")
    
    status_ui = await message_obj.reply_text(
        text="<blockquote><b>⏳ ɪɴɪᴛɪᴀᴛɪɴɢ ꜱʏꜱᴛᴇᴍ ʀᴇʙᴏᴏᴛ...</b></blockquote>\n\n<b>ᴛᴇʀᴍɪɴᴀᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ ᴀɴᴅ ᴄʟᴇᴀʀɪɴɢ ᴄᴀᴄʜᴇ...</b>",
        quote=True
    )
    
    await asyncio.sleep(5)
    await status_ui.edit("<blockquote><b>✅ ꜱᴇʀᴠᴇʀ ʀᴇꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b></blockquote>\n\n<b>🛡️ ɴᴇᴛᴡᴏʀᴋ ɪꜱ ɴᴏᴡ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ.</b>")
    
    # Execute OS level restart
    os.execl(sys.executable, sys.executable, *sys.argv)
    
# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🎛️ ᴜɪ ɴᴀᴠɪɢᴀᴛɪᴏɴ ʀᴏᴜᴛᴇʀꜱ (ᴄᴀʟʟʙᴀᴄᴋ ʜᴀɴᴅʟᴇʀꜱ)
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_callback_query(filters.regex(r'^help'))
async def route_help_menu(bot, query):
    """ Routes the user to the Network Help Panel. """
    help_layout = InlineKeyboardMarkup([
        [InlineKeyboardButton('🛠️ ᴏᴘᴇʀᴀᴛɪᴏɴ ɢᴜɪᴅᴇ 🛠️', callback_data='how_to_use')],
        [
            InlineKeyboardButton('⚙️ ꜱᴇᴛᴛɪɴɢꜱ ⚙️', callback_data='settings#main'),
            InlineKeyboardButton('📊 ɴᴇᴛᴡᴏʀᴋ ꜱᴛᴀᴛꜱ 📊', callback_data='status')
        ],
        [InlineKeyboardButton('🔙 ʀᴇᴛᴜʀɴ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ', callback_data='back')]
    ])
    
    await query.message.edit_text(
        text=Translation.HELP_TXT,
        reply_markup=help_layout
    )

@Client.on_callback_query(filters.regex(r'^how_to_use'))
async def route_guide_menu(bot, query):
    """ Routes the user to the Operational Guidelines. """
    guide_layout = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔙 ʀᴇᴛᴜʀɴ', callback_data='help')]
    ])
    
    await query.message.edit_text(
        text=Translation.HOW_USE_TXT,
        reply_markup=guide_layout,
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'^back'))
async def route_main_menu(bot, query):
    """ Returns the user to the Core Initialization Panel. """
    await query.message.edit_text(
       text=Translation.START_TXT.format(query.from_user.first_name),
       reply_markup=InlineKeyboardMarkup(SYSTEM_MAIN_BUTTONS)
    )

@Client.on_callback_query(filters.regex(r'^about'))
async def route_about_menu(bot, query):
    """ Routes the user to the System Information Panel. """
    about_layout = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔙 ʀᴇᴛᴜʀɴ ᴛᴏ ᴍᴀɪɴ ᴍᴇɴᴜ', callback_data='back')]
    ])
    
    await query.message.edit_text(
        text=Translation.ABOUT_TXT.format(bot.me.mention),
        reply_markup=about_layout,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML,
    )

@Client.on_callback_query(filters.regex(r'^status'))
async def route_system_status(bot, query):
    """ Routes the user to the Network Statistics Dashboard. """
    users_count, bots_count = await db.total_users_bots_count()
    total_channels = await db.total_channels()
    
    status_layout = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔙 ʀᴇᴛᴜʀɴ', callback_data='help')]
    ])
    
    await query.message.edit_text(
        text=Translation.STATUS_TXT.format(users_count, bots_count, temp.forwardings),
        reply_markup=status_layout,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )
    
# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🏁 ᴇɴᴅ ᴏꜰ ꜰɪʟᴇ : ꜱʏꜱᴛᴇᴍ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ ᴄᴏʀᴇ
# ------------------------------------------------------------------------------------------------------------------------------------------------
