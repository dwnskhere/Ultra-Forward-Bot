# █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
# █ 🛡️ ɴᴇᴛᴡᴏʀᴋ ᴄʟɪᴇɴᴛ ᴍᴀɴᴀɢᴇʀ ᴠ3.0
# █ 🎯 ᴏᴡɴᴇᴅ & ᴏᴘᴇʀᴀᴛᴇᴅ ʙʏ @IND_BOTZ 
# █ ⚠️ ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ - ᴘʀɪᴠᴀᴛᴇ ᴇᴅɪᴛɪᴏɴ
# █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

import os
import re 
import sys
import typing
import asyncio 
import logging 
from typing import Union, Optional, AsyncGenerator
from pyrogram import Client, filters
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait

from database import db 
from config import Config, temp
from translation import Translation

# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ɢʟᴏʙᴀʟ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴꜱ & ʀᴇɢᴇx
# ------------------------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sys_logger = logging.getLogger("IND_CLIENT_CORE")
sys_logger.setLevel(logging.INFO)

INLINE_PAYLOAD_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:/{0,2}(.+?)(:same)?])")
AUTH_TOKEN_PROMPT = "<blockquote><b><u>🤖 ʙᴏᴛ ɴᴏᴅᴇ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ</u></b></blockquote>\n\n<b>1) ᴄʀᴇᴀᴛᴇ ᴀ ɴᴇᴡ ʙᴏᴛ ᴠɪᴀ @BotFather</b>\n<b>2) ᴄᴏᴘʏ ᴛʜᴇ ᴀᴘɪ ᴛᴏᴋᴇɴ ᴘʀᴏᴠɪᴅᴇᴅ.</b>\n<b>3) ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ᴘᴀꜱᴛᴇ ᴛʜᴇ ᴛᴏᴋᴇɴ ʜᴇʀᴇ.</b>\n\n<b>🛡️ @IND_BOTZ</b>"
MAX_SESSION_LENGTH = 351

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🚀 ᴄᴏʀᴇ ᴇɴɢɪɴᴇ: ɴᴏᴅᴇ ʙᴏᴏᴛɪɴɢ & ɪᴛᴇʀᴀᴛɪᴏɴ
# ------------------------------------------------------------------------------------------------------------------------------------------------

async def start_clone_bot(NodeEngine, data=None):
   """ Initializes the bot node and injects a custom sequential message iterator. """
   await NodeEngine.start()
   
   async def custom_message_iterator(
      self,
      chat_id: Union[int, str],
      limit: int,
      offset: int = 0,
      search: str = None,
      filter: "types.TypeMessagesFilter" = None,
      ) -> Optional[AsyncGenerator["types.Message", None]]:
        """
        Iterate source message IDs in ascending order.

        `limit` is the final source message ID boundary and `offset` is the
        last ID already confirmed. The next requested ID is therefore offset+1.
        Advancing by the requested ID range (not response length) avoids the
        old inclusive-boundary overlap and prevents empty/deleted IDs from
        trapping the iterator in the same range forever.
        """
        current_id = max(0, int(offset or 0))
        final_id = max(0, int(limit or 0))
        while current_id < final_id:
            batch_end = min(final_id, current_id + 200)
            requested_ids = list(range(max(1, current_id + 1), batch_end + 1))
            if not requested_ids:
                return
            fetched_messages = await self.get_messages(chat_id, requested_ids)
            if not isinstance(fetched_messages, (list, tuple)):
                fetched_messages = [fetched_messages] if fetched_messages else []
            # Source IDs must be yielded in ascending order: the durable cursor is
            # monotonic, so reverse-ordered API results could skip unprocessed IDs.
            fetched_messages = sorted(
                (item for item in fetched_messages if item is not None),
                key=lambda item: int(getattr(item, "id", 0) or 0),
            )
            for single_msg in fetched_messages:
                if single_msg is not None:
                    yield single_msg
            current_id = batch_end

   NodeEngine.iter_messages = custom_message_iterator
   return NodeEngine

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🛡️ ɴᴇᴛᴡᴏʀᴋ ᴄʟɪᴇɴᴛ ᴍᴀɴᴀɢᴇʀ ᴄʟᴀꜱꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------

class CLIENT: 
  """ Advanced Network Manager handling both Bot and Userbot Pyrogram sessions dynamically. """
  
  def __init__(self):
     self.api_id = Config.API_ID
     self.api_hash = Config.API_HASH
    
  def client(self, auth_data, is_user_node=None):
     """ Generates a Pyrogram client instance dynamically based on node type. """
     if is_user_node == None and auth_data.get('is_bot') == False:
        return Client("IND_USER_NODE", self.api_id, self.api_hash, session_string=auth_data.get('session'))
     elif is_user_node == True:
        return Client("IND_USER_NODE", self.api_id, self.api_hash, session_string=auth_data)
     elif is_user_node != False:
        auth_data = auth_data.get('token')
     return Client("IND_BOT_NODE", self.api_id, self.api_hash, bot_token=auth_data, in_memory=True)
  
  async def add_bot(self, core_bot, message):
     """ Authenticates and registers a new Bot token into the database. """
     client_id = int(message.from_user.id)
     prompt_msg = await core_bot.ask(chat_id=client_id, text=AUTH_TOKEN_PROMPT)
     
     if prompt_msg.text == '/cancel':
        return await prompt_msg.reply('<b>❌ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴀʙᴏʀᴛᴇᴅ !</b>')
     elif not prompt_msg.forward_date:
       return await prompt_msg.reply_text("<b>🚫 ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ᴀ ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʙᴏᴛꜰᴀᴛʜᴇʀ.</b>")
     elif str(prompt_msg.forward_from.id) != "93372553":
       return await prompt_msg.reply_text("<b>🚫 ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ꜱᴏᴜʀᴄᴇ. ᴍᴜꜱᴛ ʙᴇ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ @BotFather.</b>")
       
     extracted_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', prompt_msg.text, re.IGNORECASE)
     extracted_token = extracted_token[0] if extracted_token else None
     
     if not extracted_token:
       return await prompt_msg.reply_text("<b>🚫 ɴᴏ ᴠᴀʟɪᴅ ᴀᴘɪ ᴛᴏᴋᴇɴ ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ.</b>")
       
     try:
       active_client = await start_clone_bot(self.client(extracted_token, False), True)
     except Exception as err:
       await prompt_msg.reply_text(f"<b>❌ ɴᴏᴅᴇ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ:</b>\n`{err}`")
       
     node_info = active_client.me
     db_payload = {
       'id': node_info.id,
       'is_bot': True,
       'user_id': client_id,
       'name': node_info.first_name,
       'token': extracted_token,
       'username': node_info.username 
     }
     await db.add_bot(db_payload)
     return True
    
  async def add_session(self, core_bot, message):
     """ Authenticates and registers a Pyrogram String Session (Userbot). """
     client_id = int(message.from_user.id)
     warning_txt = "<blockquote><b><u>⚠️ ꜱᴇᴄᴜʀɪᴛʏ ᴡᴀʀɴɪɴɢ ⚠️</u></b></blockquote>\n\n<b>ᴜꜱɪɴɢ ᴀ ᴜꜱᴇʀʙᴏᴛ ᴀʟʟᴏᴡꜱ ᴇxᴛʀᴀᴄᴛɪᴏɴ ꜰʀᴏᴍ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ. ʜᴏᴡᴇᴠᴇʀ, ᴀᴅᴅ ʏᴏᴜʀ ᴘʏʀᴏɢʀᴀᴍ ꜱᴇꜱꜱɪᴏɴ ᴀᴛ ʏᴏᴜʀ ᴏᴡɴ ʀɪꜱᴋ. ᴡᴇ ᴀʀᴇ ɴᴏᴛ ʀᴇꜱᴘᴏɴꜱɪʙʟᴇ ꜰᴏʀ ᴀɴʏ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴꜱ.</b>\n\n<b>🛡️ @IND_BOTZ</b>"
     await core_bot.send_message(client_id, text=warning_txt)
     
     prompt_msg = await core_bot.ask(chat_id=client_id, text="<b>🎯 ꜱᴜʙᴍɪᴛ ʏᴏᴜʀ ᴘʏʀᴏɢʀᴀᴍ ᴠ2 ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ.</b>\n\n<code>/cancel</code> - <b>ᴀʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ</b>")
     
     if prompt_msg.text == '/cancel':
        return await prompt_msg.reply('<b>❌ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴀʙᴏʀᴛᴇᴅ !</b>')
     elif len(prompt_msg.text) < MAX_SESSION_LENGTH:
        return await prompt_msg.reply('<b>🚫 ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ.</b>')
        
     try:
       user_client = await start_clone_bot(self.client(prompt_msg.text, True), True)
     except Exception as err:
       await prompt_msg.reply_text(f"<b>❌ ᴜꜱᴇʀ ɴᴏᴅᴇ ᴇʀʀᴏʀ:</b>\n`{err}`")
       
     user_info = user_client.me
     db_payload = {
       'id': user_info.id,
       'is_bot': False,
       'user_id': client_id,
       'name': user_info.first_name,
       'session': prompt_msg.text,
       'username': user_info.username
     }
     await db.add_bot(db_payload)
     return True
    
# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ꜱʏꜱᴛᴇᴍ ᴄᴏᴍᴍᴀɴᴅꜱ & ᴄᴏɴꜰɪɢ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_message(filters.private & filters.command('reset'))
async def reset_user_settings(bot, message):
    """ Restores individual user configurations to default. """
    default_config = await db.get_configs("01")
    temp.CONFIGS[message.from_user.id] = default_config
    await db.update_configs(message.from_user.id, default_config)
    await message.reply("<blockquote><b>✅ ꜱʏꜱᴛᴇᴍ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ ʀᴇꜱᴛᴏʀᴇᴅ ᴛᴏ ꜰᴀᴄᴛᴏʀʏ ᴅᴇꜰᴀᴜʟᴛꜱ.</b></blockquote>\n\n<b>🛡️ @IND_BOTZ</b>")

@Client.on_message(filters.command('resetall') & filters.user(Config.OWNER_ID))
async def master_reset_all(bot, message):
  """ Admin command to wipe all users' database configurations. """
  all_users = await db.get_all_users()
  status_msg = await message.reply("<b>⏳ ɪɴɪᴛɪᴀᴛɪɴɢ ɢʟᴏʙᴀʟ ɴᴇᴛᴡᴏʀᴋ ʀᴇꜱᴇᴛ...</b>")
  
  format_txt = "<b><u>🌐 ɢʟᴏʙᴀʟ ʀᴇꜱᴇᴛ ꜱᴛᴀᴛᴜꜱ</u></b>\n\n<b>📦 ᴛᴏᴛᴀʟ ɴᴏᴅᴇꜱ:</b> {}\n<b>✅ ꜱᴜᴄᴄᴇꜱꜱ:</b> {}\n<b>❌ ꜰᴀɪʟᴇᴅ:</b> {}\n\n<b>🛡️ @IND_BOTZ</b>"
  total = success = failed = 0
  error_logs = []
  
  async for user_data in all_users:
      uid = user_data['id']
      default_params = await get_configs(uid)
      default_params['db_uri'] = None
      total += 1
      
      if total % 10 == 0:
         await status_msg.edit(format_txt.format(total, success, failed))
         
      try: 
         await db.update_configs(uid, default_params)
         success += 1
      except Exception as err:
         error_logs.append(err)
         failed += 1
         
  if error_logs:
     await message.reply(f"<b>⚠️ ᴇʀʀᴏʀ ʟᴏɢꜱ:</b>\n`{error_logs[:100]}`")
  await status_msg.edit("<b>✅ ɢʟᴏʙᴀʟ ʀᴇꜱᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n" + format_txt.format(total, success, failed))
  
async def get_configs(client_id):
  """ Fetches current parameters of a node. """
  return await db.get_configs(client_id)

async def update_configs(client_id, param_key, param_val):
  """ Safely modifies the database parameters for a user. """
  current_params = await db.get_configs(client_id)
  if param_key in ['caption', 'duplicate', 'db_uri', 'forward_tag', 'protect', 'file_size', 'size_limit', 'extension', 'keywords', 'button']:
     current_params[param_key] = param_val
  else: 
     current_params['filters'][param_key] = param_val
     
  await db.update_configs(client_id, current_params)
    
def parse_buttons(raw_text, markup=True):
    """ 
    Advanced payload parser.
    Extracts custom inline button syntax and converts them to Pyrogram Keyboards.
    """
    button_matrix = []
    for match_obj in INLINE_PAYLOAD_REGEX.finditer(raw_text):
        escape_count = 0
        validation_idx = match_obj.start(1) - 1
        
        while validation_idx > 0 and raw_text[validation_idx] == "\\":
            escape_count += 1
            validation_idx -= 1

        if escape_count % 2 == 0:
            if bool(match_obj.group(4)) and button_matrix:
                button_matrix[-1].append(InlineKeyboardButton(
                    text=match_obj.group(2),
                    url=match_obj.group(3).replace(" ", "")))
            else:
                button_matrix.append([InlineKeyboardButton(
                    text=match_obj.group(2),
                    url=match_obj.group(3).replace(" ", ""))])
                    
    if markup and button_matrix:
       button_matrix = InlineKeyboardMarkup(button_matrix)
    return button_matrix if button_matrix else None

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🏁 ᴇɴᴅ ᴏꜰ ꜰɪʟᴇ : ɴᴇᴛᴡᴏʀᴋ ᴄʟɪᴇɴᴛ ᴍᴀɴᴀɢᴇʀ
# ------------------------------------------------------------------------------------------------------------------------------------------------
