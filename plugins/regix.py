# █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
# █ 🛡️ ᴜʟᴛɪᴍᴀᴛᴇ ꜰᴏʀᴡᴀʀᴅɪɴɢ ᴇɴɢɪɴᴇ ᴄᴏʀᴇ ᴠ5.0 [ᴇɴᴛᴇʀᴘʀɪꜱᴇ ᴇᴅɪᴛɪᴏɴ]
# █ 🎯 ᴏᴡɴᴇᴅ & ᴏᴘᴇʀᴀᴛᴇᴅ ʙʏ @IND_BOTZ 
# █ ⚠️ ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ - ᴘʀɪᴠᴀᴛᴇ & ʜɪɢʜʟʏ ꜱᴇᴄᴜʀᴇᴅ ᴇᴅɪᴛɪᴏɴ
# █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

import os
import sys 
import math
import time
import asyncio 
import logging
from .utils import STS
from database import db 
from .test import CLIENT, start_clone_bot
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ɢʟᴏʙᴀʟ ꜱʏꜱᴛᴇᴍ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ & ʟᴏɢɢɪɴɢ ᴘʀᴏᴛᴏᴄᴏʟꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------

IND_SYS_CLIENT = CLIENT()

# Advanced Enterprise Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [IND_CORE_ENGINE] - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
sys_logger = logging.getLogger(__name__)
sys_logger.setLevel(logging.INFO)

# Fetching the core text format from Translation
CORE_FORMAT_TEXT = Translation.TEXT

# Premium Popup Status format in Small Caps
PREMIUM_PROGRESS_POPUP = """
<blockquote><b><u>📊 ʟɪᴠᴇ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ꜱᴛᴀᴛᴜꜱ</u></b></blockquote>

📈 <b>ᴘᴇʀᴄᴇɴᴛᴀɢᴇ :</b> <code>{0} %</code>

♻️ <b>ꜰᴇᴛᴄʜᴇᴅ ᴅᴀᴛᴀ :</b> <code>{1}</code>
🔥 <b>ꜰᴏʀᴡᴀʀᴅᴇᴅ :</b> <code>{2}</code>
🫠 <b>ʀᴇᴍᴀɪɴɪɴɢ :</b> <code>{3}</code>

📊 <b>ᴄᴜʀʀᴇɴᴛ ꜱᴛᴀᴛᴜꜱ :</b> <code>{4}</code>
⏳️ <b>ᴇꜱᴛɪᴍᴀᴛᴇᴅ ᴛɪᴍᴇ :</b> <code>{5}</code>

<b>🛡️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @IND_BOTZ</b>
"""

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🚀 ᴍᴀɪɴ ᴇxᴇᴄᴜᴛɪᴏɴ ʙʟᴏᴄᴋ: ᴘᴜʙʟɪᴄ ꜰᴏʀᴡᴀʀᴅ ᴇɴɢɪɴᴇ
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_callback_query(filters.regex(r'^start_public'))
async def execute_public_forwarding(bot, callback_query):
    """
    Core function to handle forwarding requests, initialize node connections, 
    and manage batch processing of messages securely.
    """
    client_id = callback_query.from_user.id
    temp.CANCEL[client_id] = False
    transmission_id = callback_query.data.split("_")[2]
    
    # Task Lock Security Verification
    if temp.lock.get(client_id) and str(temp.lock.get(client_id)) == "True":
        sys_logger.warning(f"Client {client_id} attempted parallel execution. Blocked.")
        return await callback_query.answer("⚠️ ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ʏᴏᴜʀ ᴘʀᴇᴠɪᴏᴜꜱ ᴛᴀꜱᴋ ɪꜱ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!", show_alert=True)
        
    transmission_state = STS(transmission_id)
    if not transmission_state.verify():
        await callback_query.answer("🚫 ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ꜱᴇꜱꜱɪᴏɴ. ᴘʟᴇᴀꜱᴇ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ɴᴇᴡ ʀᴇQᴜᴇꜱᴛ.", show_alert=True)
        return await callback_query.message.delete()
        
    session_data = transmission_state.get(full=True)
    
    # Target Zone Overlap Protection
    if session_data.TO in temp.IS_FRWD_CHAT:
        return await callback_query.answer("⛔ ᴀ ᴛᴀꜱᴋ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ ɪɴ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴢᴏɴᴇ. ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ.", show_alert=True)
        
    status_msg = await edit_display_msg(callback_query.message, "<blockquote><b><u>🔄 ᴠᴇʀɪꜰʏɪɴɢ ꜱʏꜱᴛᴇᴍ ᴅᴀᴛᴀ... ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</u></b></blockquote>\n\n<b>🛡️ @IND_BOTZ</b>")
    
    # Fetch Configurations
    active_node, cap_payload, tag_flag, metadata, protect_flag, inline_btn = await transmission_state.get_data(client_id)
    
    if not active_node:
        return await edit_display_msg(status_msg, "<b>🚫 ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴛᴛᴀᴄʜ ᴀɴʏ ʙᴏᴛ/ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ <code>/settings</code> ᴛᴏ ᴀᴅᴅ ᴏɴᴇ.</b>", wait=True)
        
    # Booting up Node Engine
    try:
        sys_logger.info(f"Booting node for client {client_id}")
        node_client = await start_clone_bot(IND_SYS_CLIENT.client(active_node))
    except Exception as node_err:  
        sys_logger.error(f"Node Boot Failure: {node_err}")
        return await status_msg.edit(f"<b>❌ ɴᴏᴅᴇ ᴇʀʀᴏʀ:</b>\n`{node_err}`")
        
    await edit_display_msg(status_msg, "<b>⏳ ᴇꜱᴛᴀʙʟɪꜱʜɪɴɢ ꜱᴇᴄᴜʀᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ...</b>")
    
    # Source Verification Phase
    try: 
       await node_client.get_messages(transmission_state.get("FROM"), transmission_state.get("limit"))
    except Exception as src_err:
       sys_logger.error(f"Source access denied: {src_err}")
       err_txt = f"<b>🚫 ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ ᴛᴏ ꜱᴏᴜʀᴄᴇ ᴢᴏɴᴇ.</b>\n\n<i>ɪꜰ ɪᴛꜱ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ, ᴇɴꜱᴜʀᴇ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ᴀ ᴍᴇᴍʙᴇʀ ᴏʀ ʏᴏᴜʀ ʙᴏᴛ [t.me/{active_node['username']}] ɪꜱ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ.</i>"
       await edit_display_msg(status_msg, err_txt, generate_retry_btn(transmission_id), True)
       return await terminate_node(node_client, client_id)
       
    # Destination Verification Phase
    try:
       test_msg = await node_client.send_message(session_data.TO, "<i>⚡ System Core Ping...</i>")
       await test_msg.delete()
    except Exception as dest_err:
       sys_logger.error(f"Target access denied: {dest_err}")
       err_txt = f"<b>🚫 ᴡʀɪᴛᴇ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ.</b>\n\n<i>ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ʏᴏᴜʀ ɴᴏᴅᴇ [t.me/{active_node['username']}] ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴢᴏɴᴇ ᴡɪᴛʜ ꜰᴜʟʟ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ.</i>"
       await edit_display_msg(status_msg, err_txt, generate_retry_btn(transmission_id), True)
       return await terminate_node(node_client, client_id)
       
    # Ready for Transmission
    temp.forwardings += 1
    await db.add_frwd(client_id)
    task_id = str(transmission_id)
    await db.ensure_forwarding_indexes()
    node_configs = await db.get_configs(client_id)
    await db.create_forwarding_task({
        "task_id": task_id, "owner_id": int(client_id),
        "source_chat_id": transmission_state.get("FROM"),
        "destination_chat_id": transmission_state.get("TO"),
        "limit": int(transmission_state.get("limit") or 0),
        "skip": int(transmission_state.get("skip") or 0),
        "start_message_id": int(transmission_state.get("skip") or 0),
        "active_node_id": active_node.get("id"),
        "active_node_is_bot": bool(active_node.get("is_bot")),
        "forward_tag": bool(tag_flag), "protect_content": bool(protect_flag),
        "caption_template": cap_payload, "button_payload": node_configs.get("button"),
        "settings_snapshot": metadata,
        "transmission_id": str(transmission_id),
    })
    claimed_task = await db.claim_forwarding_task(task_id)
    if not claimed_task:
        await edit_display_msg(status_msg, "<b>⚠️ ᴛʜɪꜱ ᴛᴀꜱᴋ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʙᴇɪɴɢ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ʙʏ ᴀɴᴏᴛʜᴇʀ ᴡᴏʀᴋᴇʀ.</b>")
        return await terminate_node(node_client, client_id)

    # Continue strictly after the last persisted source ID, restoring durable counters.
    resume_cursor = int(claimed_task.get("last_confirmed_message_id",
                                         claimed_task.get("cursor_message_id", 0)) or 0)
    cached_state = transmission_state.get()
    cached_state["fetched"] = resume_cursor
    persisted_counts = claimed_task.get("counts", {})
    cached_state["total_files"] = int(persisted_counts.get("forwarded", 0))
    cached_state["deleted"] = int(persisted_counts.get("failed", 0))
    cached_state["duplicate"] = int(persisted_counts.get("skipped", 0))
    await dispatch_alert(node_client, client_id, "<b>🚀 ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ᴇɴɢɪɴᴇ ɪɢɴɪᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>")
    
    transmission_state.add(time=True)
    throttle_sleep = 1 if active_node['is_bot'] else 10
    await edit_display_msg(status_msg, "<b>⚡ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴅᴀᴛᴀ...</b>") 
    
    temp.IS_FRWD_CHAT.append(session_data.TO)
    temp.lock[client_id] = True
    
    # Core Loop
    if temp.lock[client_id]:
        try:
          MESSAGE_BATCH_QUEUE = []
          loop_counter = 0
          
          await refresh_ui_status(status_msg, 'ᴘʀᴏɢʀᴇꜱꜱɪɴɢ', 10, transmission_state)
          sys_logger.info(f"FORWARDING STARTED | SRC: {transmission_state.get('FROM')} | DEST: {transmission_state.get('TO')} | TOTAL: {transmission_state.get('limit')}")
          
          async for msg_obj in node_client.iter_messages(
            node_client,
            chat_id=transmission_state.get('FROM'), 
            limit=int(transmission_state.get('limit')), 
            offset=resume_cursor
            ):
                # Check for kill switch
                if await verify_kill_switch(node_client, client_id, status_msg, transmission_state):
                   return
                   
                # Throttle UI Updates
                if loop_counter % 20 == 0: 
                   await refresh_ui_status(status_msg, 'ᴘʀᴏɢʀᴇꜱꜱɪɴɢ', 10, transmission_state)
                loop_counter += 1
                transmission_state.add('fetched')
                
                # Filter Handlers
                if msg_obj == "DUPLICATE":
                   transmission_state.add('duplicate')
                   continue
                elif msg_obj == "FILTERED":
                   transmission_state.add('filtered')
                   continue
                if msg_obj.empty or msg_obj.service:
                   transmission_state.add('deleted')
                   await db.checkpoint_forwarding_message(task_id, msg_obj.id, "skipped", "empty_or_service")
                   continue
                   
                # Forwarding Protocol (With tag)
                if tag_flag:
                   MESSAGE_BATCH_QUEUE.append(msg_obj.id)
                   queue_size = len(MESSAGE_BATCH_QUEUE)
                   remaining_items = transmission_state.get('total') - transmission_state.get('fetched')
                   
                   # Batch dispatcher
                   if (queue_size >= 100 or remaining_items <= 100): 
                      batch_ids = list(MESSAGE_BATCH_QUEUE)
                      batch_ok = await execute_batch_forward(node_client, batch_ids, status_msg, transmission_state, protect_flag)
                      for source_message_id in batch_ids:
                         await db.checkpoint_forwarding_message(task_id, source_message_id, "forwarded" if batch_ok else "failed", None if batch_ok else "batch forward failed")
                      if batch_ok:
                         transmission_state.add('total_files', queue_size)
                      await asyncio.sleep(10)
                      MESSAGE_BATCH_QUEUE = []
                      
                # Copy Protocol (Without tag / Custom Caption)
                else:
                   formatted_caption = format_custom_caption(msg_obj, cap_payload)
                   extracted_details = {
                       "msg_id": msg_obj.id, 
                       "media": extract_media_id(msg_obj), 
                       "caption": formatted_caption, 
                       'button': inline_btn, 
                       "protect": protect_flag
                   }
                   copied = await execute_single_copy(node_client, extracted_details, status_msg, transmission_state)
                   if copied:
                      transmission_state.add('total_files')
                      await db.checkpoint_forwarding_message(task_id, msg_obj.id, "forwarded")
                   else:
                      await db.checkpoint_forwarding_message(task_id, msg_obj.id, "failed", "copy failed; see worker logs")
                   await asyncio.sleep(throttle_sleep)
                   
        except Exception as critical_err:
            sys_logger.error(f"Critical Transmission Error: {critical_err}")
            from datetime import datetime, timedelta, timezone
            await db.update_forwarding_task(task_id, {
                "status": "interrupted",
                "last_error": str(critical_err)[:1000],
                "retry_after": datetime.now(timezone.utc) + timedelta(seconds=30),
            })
            await edit_display_msg(status_msg, f"<blockquote><b><u>❌ ꜰᴀᴛᴀʟ ꜱʏꜱᴛᴇᴍ ᴇʀʀᴏʀ</u></b></blockquote>\n\n<code>{critical_err}</code>\n\n<b>🛡️ @IND_BOTZ</b>", wait=True)
            if transmission_state.TO in temp.IS_FRWD_CHAT:
                temp.IS_FRWD_CHAT.remove(transmission_state.TO)
            return await terminate_node(node_client, client_id)
            
        # Flush a trailing partial batch even when the remaining-count estimate is off.
        if tag_flag and MESSAGE_BATCH_QUEUE:
           tail_ids = list(MESSAGE_BATCH_QUEUE)
           tail_ok = await execute_batch_forward(node_client, tail_ids, status_msg, transmission_state, protect_flag)
           for source_message_id in tail_ids:
              await db.checkpoint_forwarding_message(task_id, source_message_id, "forwarded" if tail_ok else "failed", None if tail_ok else "final batch failed")
           if tail_ok:
              transmission_state.add('total_files', len(tail_ids))
        durable_task = await db.get_forwarding_task(task_id)
        durable_counts = (durable_task or {}).get("counts", {})
        final_task_status = "completed_with_errors" if durable_counts.get("failed", 0) else "completed"
        await db.update_forwarding_task(task_id, {
            "status": final_task_status,
            "completed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        })
        # Success Cleanup
        temp.IS_FRWD_CHAT.remove(transmission_state.TO)
        await dispatch_alert(node_client, client_id, "<b>🎉 ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>")
        await refresh_ui_status(status_msg, 'ᴄᴏᴍᴘʟᴇᴛᴇᴅ', "completed", transmission_state) 
        await terminate_node(node_client, client_id)

# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ʜᴇʟᴘᴇʀ ꜰᴜɴᴄᴛɪᴏɴꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------
            
async def execute_single_copy(active_bot, msg_data, ui_msg, state_obj):
   """Copy a message, retrying transient failures without hiding terminal delivery errors."""
   for attempt in range(3):
     try:
       if msg_data.get("media") and msg_data.get("caption"):
         await active_bot.send_cached_media(
             chat_id=state_obj.get('TO'),
             file_id=msg_data.get("media"),
             caption=msg_data.get("caption"),
             reply_markup=msg_data.get('button'),
             protect_content=msg_data.get("protect"))
       else:
         await active_bot.copy_message(
             chat_id=state_obj.get('TO'),
             from_chat_id=state_obj.get('FROM'),
             caption=msg_data.get("caption"),
             message_id=msg_data.get("msg_id"),
             reply_markup=msg_data.get('button'),
             protect_content=msg_data.get("protect"))
       return True
     except FloodWait as flood_err:
       sys_logger.warning("FloodWait triggered for %s seconds.", flood_err.value)
       if ui_msg is not None:
         await refresh_ui_status(ui_msg, 'ꜱʟᴇᴇᴘɪɴɢ', flood_err.value, state_obj)
       await asyncio.sleep(flood_err.value)
       if ui_msg is not None:
         await refresh_ui_status(ui_msg, 'ᴘʀᴏɢʀᴇꜱꜱɪɴɢ', 10, state_obj)
     except RPCError as copy_err:
       sys_logger.error("Telegram copy failed: %s", copy_err)
       state_obj.add('deleted')
       return False
     except Exception as copy_err:
       sys_logger.warning("Unexpected copy error (attempt %s/3): %s", attempt + 1, copy_err)
       if attempt == 2:
         state_obj.add('deleted')
         return False
       await asyncio.sleep(2 ** attempt)
   return False


async def execute_batch_forward(active_bot, msg_batch, ui_msg, state_obj, secure_flag):
   """Forward a batch; retry unexpected transport errors at most three times."""
   for attempt in range(3):
     try:
       await active_bot.forward_messages(
           chat_id=state_obj.get('TO'),
           from_chat_id=state_obj.get('FROM'),
           protect_content=secure_flag,
           message_ids=msg_batch)
       return True
     except FloodWait as flood_err:
       sys_logger.warning("Batch forward FloodWait: %ss.", flood_err.value)
       if ui_msg is not None:
         await refresh_ui_status(ui_msg, 'ꜱʟᴇᴇᴘɪɴɢ', flood_err.value, state_obj)
       await asyncio.sleep(flood_err.value)
       if ui_msg is not None:
         await refresh_ui_status(ui_msg, 'ᴘʀᴏɢʀᴇꜱꜱɪɴɢ', 10, state_obj)
     except RPCError as batch_err:
       sys_logger.error("Telegram batch forward failed: %s", batch_err)
       return False
     except Exception as batch_err:
       sys_logger.warning("Unexpected batch forward error (attempt %s/3): %s", attempt + 1, batch_err)
       if attempt == 2:
         return False
       await asyncio.sleep(2 ** attempt)
   return False

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🎨 ᴜɪ / ꜱᴛᴀᴛᴜꜱ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ꜰᴜɴᴄᴛɪᴏɴꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------

async def edit_display_msg(message_obj, new_text, inline_btn=None, wait=None):
    """ Enterprise-grade message editor to prevent MessageNotModified exceptions. """
    try:
        return await message_obj.edit(new_text, reply_markup=inline_btn)
    except MessageNotModified:
        pass 
    except FloodWait as flood_err:
        if wait:
           sys_logger.info(f"UI Update Rate Limit. Sleeping for {flood_err.value}s")
           await asyncio.sleep(flood_err.value)
           return await edit_display_msg(message_obj, new_text, inline_btn, wait)
        
async def refresh_ui_status(message_obj, header_title, current_status, state_obj):
   """ Dynamic UI Status Builder generating advanced progress bars. """
   state_data = state_obj.get(full=True)
   
   ui_status_txt = 'ꜰᴏʀᴡᴀʀᴅɪɴɢ' if current_status == 10 else f"ꜱʟᴇᴇᴘɪɴɢ {current_status} ꜱ" if str(current_status).isnumeric() else current_status
   calc_percentage = "{:.0f}".format(float(state_data.fetched) * 100 / float(state_data.total))
   
   current_time = time.time()
   time_diff = int(current_time - state_data.start)
   exec_speed = state_obj.divide(state_data.fetched, time_diff)
   
   elapsed_ms = round(time_diff) * 1000
   completion_ms = round(state_obj.divide(state_data.total - state_data.fetched, int(exec_speed))) * 1000
   total_est_ms = elapsed_ms + completion_ms  
   
   # Advanced Progress Bar Graphics
   graphic_bar = "▰{0}{1}".format(
       ''.join(["▰" for i in range(math.floor(int(calc_percentage) / 10))]),
       ''.join(["▱" for i in range(10 - math.floor(int(calc_percentage) / 10))])
   )
   
   btn_layout =  [[InlineKeyboardButton(header_title, f'fwrdstatus#{ui_status_txt}#{total_est_ms}#{calc_percentage}#{state_data.id}')]]
   
   formatted_eta = format_time_readable(milliseconds=total_est_ms)
   formatted_eta = formatted_eta if formatted_eta != '' else '0 ꜱ'

   # Injecting dynamic data into Translation format
   final_text = CORE_FORMAT_TEXT.format(
       state_data.fetched, 
       state_data.total_files, 
       state_data.duplicate, 
       state_data.deleted, 
       state_data.skip, 
       ui_status_txt, 
       calc_percentage, 
       formatted_eta, 
       graphic_bar
   )
   
   if current_status in ["cancelled", "completed"]:
      btn_layout.append([
         InlineKeyboardButton('📢 ᴏꜰꜰɪᴄɪᴀʟ ᴜᴘᴅᴀᴛᴇꜱ', url='https://t.me/IND_BOTZ'),
         InlineKeyboardButton('💬 ɴᴇᴛᴡᴏʀᴋ ꜱᴜᴘᴘᴏʀᴛ', url='https://t.me/IND_BOTZ')
      ])
   else:
      btn_layout.append([InlineKeyboardButton('✖️ ᴀʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ ✖️', 'terminate_frwd')])
      
   await edit_display_msg(message_obj, final_text, InlineKeyboardMarkup(btn_layout))

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🛑 ꜱᴇᴄᴜʀɪᴛʏ & ᴄʟᴇᴀɴᴜᴘ ᴄᴏɴᴛʀᴏʟꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------
   
async def verify_kill_switch(active_bot, client_id, ui_msg, state_obj):
   """ Verifies if the user requested a task cancellation and executes cleanup. """
   if temp.CANCEL.get(client_id) == True:
      sys_logger.info(f"Kill switch activated for client {client_id}")
      temp.IS_FRWD_CHAT.remove(state_obj.TO)
      await refresh_ui_status(ui_msg, "ᴀʙᴏʀᴛᴇᴅ", "cancelled", state_obj)
      await db.update_forwarding_task(str(state_obj.id), {"status": "cancelled"})
      await dispatch_alert(active_bot, client_id, "<b>❌ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ᴀʙᴏʀᴛᴇᴅ ʙʏ ᴜꜱᴇʀ.</b>")
      await terminate_node(active_bot, client_id)
      return True 
   return False 

async def terminate_node(active_bot, client_id):
   """ Safely powers down the active bot node and clears memory locks. """
   try:
     await active_bot.stop()
   except Exception as err:
     sys_logger.error(f"Error terminating node: {err}")
     pass 
     
   await db.rmve_frwd(client_id)
   temp.forwardings -= 1
   temp.lock[client_id] = False 
   sys_logger.info(f"Node fully terminated for client {client_id}")
    
async def dispatch_alert(active_bot, client_id, text_msg):
   """ Dispatches an alert message directly to the user's inbox securely. """
   try:
      await active_bot.send_message(client_id, text=text_msg)
   except:
      pass 

# ------------------------------------------------------------------------------------------------------------------------------------------------
# ⚙️ ᴅᴀᴛᴀ ꜰᴏʀᴍᴀᴛᴛɪɴɢ ᴜᴛɪʟɪᴛɪᴇꜱ
# ------------------------------------------------------------------------------------------------------------------------------------------------
     
def format_custom_caption(msg_obj, cap_template):
  """ Formats the custom caption injecting dynamic file details. """
  if msg_obj.media:
    if (msg_obj.video or msg_obj.document or msg_obj.audio or msg_obj.photo):
      media_data = getattr(msg_obj, msg_obj.media.value, None)
      if media_data:
        extracted_name = getattr(media_data, 'file_name', '')
        extracted_size = getattr(media_data, 'file_size', '')
        original_cap = getattr(msg_obj, 'caption', '')
        
        if original_cap:
          original_cap = original_cap.html
        if cap_template:
          return cap_template.format(filename=extracted_name, size=calculate_human_size(extracted_size), caption=original_cap)
        return original_cap
  return None

def calculate_human_size(raw_size):
  """ Standard bytes to Human-Readable converter algorithm. """
  size_units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
  raw_size = float(raw_size)
  idx = 0
  while raw_size >= 1024.0 and idx < len(size_units):
     idx += 1
     raw_size /= 1024.0
  return "%.2f %s" % (raw_size, size_units[idx]) 

def extract_media_id(msg_obj):
  """ Extracts exact Pyrogram file_id for direct caching. """
  if msg_obj.media:
     media_val = getattr(msg_obj, msg_obj.media.value, None)
     if media_val:
        return getattr(media_val, 'file_id', None)
  return None 

def format_time_readable(milliseconds: int) -> str:
    """ Core Time Formatter logic converting MS into clean string syntax. """
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    formatted_str = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
        
    return formatted_str[:-2]

def generate_retry_btn(transmission_id):
    """ Generates a dynamic retry button markup payload. """
    return InlineKeyboardMarkup([[InlineKeyboardButton('♻️ ʀᴇᴛʀʏ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ♻️', f"start_public_{transmission_id}")]])

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🕹️ ᴄᴀʟʟʙᴀᴄᴋ Qᴜᴇʀʏ ʜᴀɴᴅʟᴇʀꜱ (ʙᴜᴛᴛᴏɴ ᴀᴄᴛɪᴏɴꜱ)
# ------------------------------------------------------------------------------------------------------------------------------------------------

@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def trigger_kill_switch(bot, callback_obj):
    """ Instantly triggers the task termination protocol. """
    client_id = callback_obj.from_user.id 
    temp.lock[client_id] = False
    temp.CANCEL[client_id] = True 
    await callback_obj.answer("⚠️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ᴀʙᴏʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!", show_alert=True)
          
@Client.on_callback_query(filters.regex(r'^fwrdstatus'))
async def display_live_popup(bot, callback_obj):
    """ Triggers a premium popup alert showing detailed live metrics. """
    _, current_status, est_time_ms, calc_perc, tr_id = callback_obj.data.split("#")
    
    state_obj = STS(tr_id)
    if not state_obj.verify():
       items_fetched, items_forwarded, items_remaining = 0, 0, 0
    else:
       items_fetched, items_forwarded = state_obj.get('fetched'), state_obj.get('total_files')
       items_remaining = items_fetched - items_forwarded 
       
    formatted_time = format_time_readable(milliseconds=est_time_ms)
    formatted_time = formatted_time if (formatted_time != '' or current_status not in ['completed', 'cancelled']) else '0 ꜱ'
    
    return await callback_obj.answer(
        PREMIUM_PROGRESS_POPUP.format(calc_perc, items_fetched, items_forwarded, items_remaining, current_status, formatted_time), 
        show_alert=True
    )
                  
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def destroy_message_ui(bot, callback_obj):
    """ Cleanly removes the UI messages from chat interface. """
    await callback_obj.answer()
    await callback_obj.message.delete()
    await callback_obj.message.reply_to_message.delete()

# ------------------------------------------------------------------------------------------------------------------------------------------------
# 🏁 ᴇɴᴅ ᴏꜰ ꜰɪʟᴇ : ᴜʟᴛɪᴍᴀᴛᴇ ꜰᴏʀᴡᴀʀᴅɪɴɢ ᴇɴɢɪɴᴇ ᴄᴏʀᴇ
# ------------------------------------------------------------------------------------------------------------------------------------------------
