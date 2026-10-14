# 🛡️ ꜱʏꜱᴛᴇᴍ ᴄᴏʀᴇ: @IND_BOTZ
# 🎯 ᴏᴡɴᴇᴅ & ᴏᴘᴇʀᴀᴛᴇᴅ ʙʏ @IND_BOTZ
# ⚠️ ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ

import os
from config import Config

class Translation(object):
  START_TXT = """<blockquote><b>🚀 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ꜰᴏʀᴡᴀʀᴅɪɴɢ ᴇɴɢɪɴᴇ, {} !</b></blockquote>

▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

⚡ <b>ᴇxᴘᴇʀɪᴇɴᴄᴇ ꜱᴇᴀᴍʟᴇꜱꜱ ᴍᴇꜱꜱᴀɢᴇ ᴛʀᴀɴꜱꜰᴇʀꜱ ᴀᴄʀᴏꜱꜱ ᴄʜᴀɴɴᴇʟꜱ.</b>
⚙️ <b>ᴘᴏᴡᴇʀꜰᴜʟ, ꜰᴀꜱᴛ, ᴀɴᴅ ꜰᴜʟʟʏ ᴄᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ ꜰᴏʀ ʏᴏᴜʀ ɴᴇᴇᴅꜱ.</b>

🎯 <b>ᴛᴀᴘ ʜᴇʟᴘ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍʏ ᴘᴏᴡᴇʀꜱ.</b>

<blockquote><b>🛡️ ɴᴇᴛᴡᴏʀᴋ ᴍᴀɴᴀɢᴇᴅ ʙʏ @IND_BOTZ</b></blockquote>"""

  HELP_TXT = """<blockquote><b><u>🎛️ ᴀᴅᴠᴀɴᴄᴇᴅ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</u></b></blockquote>

<b><u>📌 ꜱʏꜱᴛᴇᴍ ᴄᴏᴍᴍᴀɴᴅꜱ :</u></b>
⏣ <code>/start</code> - <b>ɪɴɪᴛɪᴀʟɪᴢᴇ ᴛʜᴇ ᴇɴɢɪɴᴇ</b>
⏣ <code>/forward</code> - <b>ʙᴇɢɪɴ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ</b>
⏣ <code>/fwdstatus</code> - <b>ᴠɪᴇᴡ ᴘʀᴏɢʀᴇꜱꜱ ᴀɴᴅ ꜰᴀɪʟᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ</b>
⏣ <code>/unequify</code> - <b>ᴄʟᴇᴀɴ ᴜᴘ ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴅᴀᴛᴀ</b>
⏣ <code>/settings</code> - <b>ᴏᴘᴇɴ ᴄᴏɴꜰɪɢᴜʀᴀᴛɪᴏɴ</b>
⏣ <code>/reset</code> - <b>ʀᴇꜱᴛᴏʀᴇ ᴅᴇꜰᴀᴜʟᴛꜱ</b>

<b><u>🔥 ᴇxᴄʟᴜꜱɪᴠᴇ ᴘᴇʀᴋꜱ :</u></b>
► <b>ʙʏᴘᴀꜱꜱ ᴀᴅᴍɪɴ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ ꜰᴏʀ ᴘᴜʙʟɪᴄ ᴢᴏɴᴇꜱ.</b>
► <b>ꜱᴇᴀᴍʟᴇꜱꜱ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴇxᴛʀᴀᴄᴛɪᴏɴ ᴠɪᴀ ᴜꜱᴇʀʙᴏᴛ.</b>
► <b>ɪɴᴊᴇᴄᴛ ᴄᴜꜱᴛᴏᴍ ᴄᴀᴘᴛɪᴏɴꜱ & ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴꜱ.</b>
► <b>ᴀᴜᴛᴏ-ꜱᴋɪᴘ ʀᴇᴅᴜɴᴅᴀɴᴛ & ᴄʟᴏɴᴇᴅ ꜰɪʟᴇꜱ.</b>
► <b>ᴀᴅᴠᴀɴᴄᴇᴅ ꜰɪʟᴛᴇʀɪɴɢ ʙʏ ꜱɪᴢᴇ, ᴋᴇʏᴡᴏʀᴅ ᴏʀ ᴇxᴛᴇɴꜱɪᴏɴ.</b>

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @IND_BOTZ</b></blockquote>"""
  
  HOW_USE_TXT = """<blockquote><b><u>📖 ᴏᴘᴇʀᴀᴛɪᴏɴᴀʟ ɢᴜɪᴅᴇʟɪɴᴇꜱ :</u></b></blockquote>
  
► <b>ɪɴᴛᴇɢʀᴀᴛᴇ ᴛʜᴇ ʙᴏᴛ ᴏʀ ᴜꜱᴇʀʙᴏᴛ ɪɴᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ.</b>
► <b>ᴇɴꜱᴜʀᴇ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇꜱ ᴀʀᴇ ɢʀᴀɴᴛᴇᴅ ɪɴ ᴛʜᴇ ᴅᴇꜱᴛɪɴᴀᴛɪᴏɴ.</b>
► <b>ɴᴀᴠɪɢᴀᴛᴇ ᴛᴏ <code>/settings</code> ᴛᴏ ᴀᴛᴛᴀᴄʜ ʏᴏᴜʀ ᴄʜᴀᴛꜱ.</b>
► <b>ꜰᴏʀ ᴘʀɪᴠᴀᴛᴇ ꜱᴏᴜʀᴄᴇꜱ, ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ᴍᴜꜱᴛ ʙᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴍᴇᴍʙᴇʀ.</b>
► <b>ᴇxᴇᴄᴜᴛᴇ <code>/forward</code> ᴛᴏ ɪɢɴɪᴛᴇ ᴛʜᴇ ᴘʀᴏᴄᴇꜱꜱ.</b>
► <b>ᴜꜱᴇ <code>/fwdstatus</code> ᴛᴏ ᴄʜᴇᴄᴋ ᴄᴏᴜɴᴛꜱ, ᴛʜᴇ ʟᴀꜱᴛ ᴄʜᴇᴄᴋᴘᴏɪɴᴛ, ᴀɴᴅ ᴋɴᴏᴡɴ ꜰᴀɪʟᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ɪᴅꜱ.</b>

<blockquote><b>🛡️ @IND_BOTZ</b></blockquote>"""
  
  ABOUT_TXT = """<blockquote><b><u>⚙️ ꜱʏꜱᴛᴇᴍ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ</u></b></blockquote>

<b>🏷️ ᴅᴇꜱɪɢɴᴀᴛɪᴏɴ :</b> {}
<b>🧠 ᴄᴏʀᴇ ᴇɴɢɪɴᴇ :</b> <b>ᴀᴅᴠᴀɴᴄᴇᴅ ᴘʏ-ꜱᴄʀɪᴘᴛ</b>
<b>📡 ʜᴏꜱᴛɪɴɢ ᴢᴏɴᴇ :</b> <b>ᴘʀᴇᴍɪᴜᴍ ᴄʟᴏᴜᴅ</b>
<b>📢 ᴏꜰꜰɪᴄɪᴀʟ ʜᴜʙ :</b> <a href='https://t.me/IND_BOTZ'>@IND_BOTZ</a>
<b>🧑‍💻 ᴀʀᴄʜɪᴛᴇᴄᴛ :</b> <a href='https://t.me/IND_BOTZ'>@IND_BOTZ</a>

<blockquote><b>♻️ ᴇxᴄʟᴜꜱɪᴠᴇʟʏ ᴍᴀᴅᴇ ꜰᴏʀ @IND_BOTZ</b></blockquote>"""
  
  STATUS_TXT = """<blockquote><b><u>📈 ɴᴇᴛᴡᴏʀᴋ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</u></b></blockquote>
  
<b>👤 ᴀᴄᴛɪᴠᴇ ᴄʟɪᴇɴᴛꜱ :</b> <code>{}</code>

<b>🤖 ᴄᴏɴɴᴇᴄᴛᴇᴅ ɴᴏᴅᴇꜱ :</b> <code>{}</code>

<b>🔄 ᴛʀᴀɴꜱꜰᴇʀꜱ ᴅᴏɴᴇ :</b> <code>{}</code>

<blockquote><b>⚡ ᴍᴀɴᴀɢᴇᴅ ʙʏ @IND_BOTZ</b></blockquote>"""
  
  FROM_MSG = "<blockquote><b><u>📡 ʟᴏᴄᴀᴛᴇ ꜱᴏᴜʀᴄᴇ ᴢᴏɴᴇ</u></b></blockquote>\n\n<b>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ʟᴀꜱᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴍᴇꜱꜱᴀɢᴇ ᴏʀ ɪᴛꜱ ʟɪɴᴋ ꜰʀᴏᴍ ʏᴏᴜʀ ꜱᴏᴜʀᴄᴇ ᴄʜᴀᴛ ʜᴇʀᴇ.</b>\n<code>/cancel</code> - <b>ᴀʙᴏʀᴛ ᴛʜɪꜱ ᴏᴘᴇʀᴀᴛɪᴏɴ</b>\n\n<b>🛡️ @IND_BOTZ</b>"
  
  TO_MSG = "<blockquote><b><u>🎯 ꜱᴇʟᴇᴄᴛ ᴅᴇꜱᴛɪɴᴀᴛɪᴏɴ</u></b></blockquote>\n\n<b>ᴘɪᴄᴋ ʏᴏᴜʀ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ ꜰʀᴏᴍ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ.</b>\n<code>/cancel</code> - <b>ᴀʙᴏʀᴛ ᴛʜɪꜱ ᴏᴘᴇʀᴀᴛɪᴏɴ</b>\n\n<b>🛡️ @IND_BOTZ</b>"
  
  SKIP_MSG = "<blockquote><b><u>⏭️ ᴄᴏɴꜰɪɢᴜʀᴇ ꜱᴋɪᴘ ᴘᴀʀᴀᴍᴇᴛᴇʀꜱ</u></b></blockquote>\n\n<b>ᴇɴᴛᴇʀ ᴛʜᴇ ᴇxᴀᴄᴛ ᴀᴍᴏᴜɴᴛ ᴏꜰ ᴍᴇꜱꜱᴀɢᴇꜱ ʏᴏᴜ ᴡɪꜱʜ ᴛᴏ ʙʏᴘᴀꜱꜱ. ᴛʜᴇ ʀᴇᴍᴀɪɴᴅᴇʀ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ɴᴏʀᴍᴀʟʟʏ.</b>\n<b>ᴅᴇꜰᴀᴜʟᴛ ᴠᴀʟᴜᴇ =</b> <code>0</code>\n<code>ᴇxᴀᴍᴘʟᴇ: ɪɴᴘᴜᴛ 5 = 5 ꜰɪʟᴇꜱ ɪɢɴᴏʀᴇᴅ</code>\n<code>/cancel</code> - <b>ᴀʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ</b>\n\n<b>🛡️ @IND_BOTZ</b>"
  
  CANCEL = "<b>🚫 ᴏᴘᴇʀᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.</b>\n\n<b>♻️ @IND_BOTZ</b>"
  
  BOT_DETAILS = "<blockquote><b><u>🤖 ʙᴏᴛ ɪᴅᴇɴᴛɪᴛʏ</u></b></blockquote>\n\n<b>➣ ᴀʟɪᴀꜱ :</b> <code>{}</code>\n<b>➣ ꜱᴇʀɪᴀʟ ɪᴅ :</b> <code>{}</code>\n<b>➣ ᴜꜱᴇʀɴᴀᴍᴇ :</b> @{}\n\n<b>🛡️ @IND_BOTZ</b>"
  
  USER_DETAILS = "<blockquote><b><u>👤 ᴜꜱᴇʀʙᴏᴛ ɪᴅᴇɴᴛɪᴛʏ</u></b></blockquote>\n\n<b>➣ ᴀʟɪᴀꜱ :</b> <code>{}</code>\n<b>➣ ꜱᴇʀɪᴀʟ ɪᴅ :</b> <code>{}</code>\n<b>➣ ᴜꜱᴇʀɴᴀᴍᴇ :</b> @{}\n\n<b>🛡️ @IND_BOTZ</b>"  
         
  TEXT = """<blockquote><b><u>⏳ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ</u></b></blockquote>
  
<b>📦 ᴇxᴛʀᴀᴄᴛᴇᴅ ᴅᴀᴛᴀ :</b> <code>{}</code>

<b>✅ ᴅᴇʟɪᴠᴇʀᴇᴅ ꜱᴀꜰᴇʟʏ :</b> <code>{}</code>

<b>👥 ᴄʟᴏɴᴇꜱ ᴅᴇᴛᴇᴄᴛᴇᴅ :</b> <code>{}</code>

<b>🗑 ᴛʀᴀꜱʜᴇᴅ ꜰɪʟᴇꜱ :</b> <code>{}</code>

<b>🪆 ʙʏᴘᴀꜱꜱᴇᴅ :</b> <code>{}</code>

<b>🔁 ꜰɪʟᴛᴇʀᴇᴅ ᴏᴜᴛ :</b> <code>{}</code>

<b>📊 ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ :</b> <code>{}</code>

<b>🔥 ᴄᴏᴍᴘʟᴇᴛɪᴏɴ :</b> <code>{}</code> %

{}

<b>♻️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @IND_BOTZ</b>
"""

  TEXT1 = """<blockquote><b><u>✅ ᴛʀᴀɴꜱᴍɪꜱꜱɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u></b></blockquote>

<b>📦 ᴛᴏᴛᴀʟ ᴇxᴛʀᴀᴄᴛᴇᴅ :</b> <code>{}</code>

<b>✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟɪᴠᴇʀᴇᴅ :</b> <code>{}</code>

<b>👥 ᴄʟᴏɴᴇꜱ ꜰᴏᴜɴᴅ :</b> <code>{}</code>

<b>🗑 ᴛʀᴀꜱʜᴇᴅ :</b> <code>{}</code>

<b>🪆 ʙʏᴘᴀꜱꜱᴇᴅ :</b> <code>{}</code>

<b>📊 ꜰɪɴᴀʟ ꜱᴛᴀᴛꜱ :</b> <code>{}</code>

<b>⏳ ᴡᴏʀᴋ ᴘʀᴏɢʀᴇꜱꜱ :</b> <code>{}</code>

<b>⏰ ᴇꜱᴛɪᴍᴀᴛᴇᴅ ᴛɪᴍᴇ :</b> <code>{}</code>

{}

<b>♻️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @IND_BOTZ</b>"""

  DUPLICATE_TEXT = """<blockquote><b><u>🧹 ᴄʟᴇᴀɴᴜᴘ ʀᴇᴘᴏʀᴛ</u></b></blockquote>

<b>📦 ꜱᴄᴀɴɴᴇᴅ ꜰɪʟᴇꜱ :</b> <code>{}</code>

<b>🗑 ᴅᴜᴘʟɪᴄᴀᴛᴇꜱ ᴡɪᴘᴇᴅ :</b> <code>{}</code>

{}

<b>🛡️ @IND_BOTZ</b>
"""
  DOUBLE_CHECK = """<blockquote><b><u>⚠️ ꜰɪɴᴀʟ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ</u></b></blockquote>
  
<b>ᴘʟᴇᴀꜱᴇ ᴄᴏɴꜰɪʀᴍ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴘᴀʀᴀᴍᴇᴛᴇʀꜱ ʙᴇꜰᴏʀᴇ ɪɴɪᴛɪᴀᴛɪɴɢ ᴛʜᴇ ᴛʀᴀɴꜱꜰᴇʀ:</b>

<b>★ ᴀᴄᴛɪᴠᴇ ᴇɴɢɪɴᴇ :</b> [{botname}](t.me/{botuname})
<b>★ ꜱᴏᴜʀᴄᴇ ᴢᴏɴᴇ :</b> <code>{from_chat}</code>
<b>★ ᴛᴀʀɢᴇᴛ ᴢᴏɴᴇ :</b> <code>{to_chat}</code>
<b>★ ʙʏᴘᴀꜱꜱ ᴄᴏᴜɴᴛ :</b> <code>{skip}</code>

<i>° ᴇɴꜱᴜʀᴇ [{botname}](t.me/{botuname}) ʜᴏʟᴅꜱ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ ɪɴ ᴛʜᴇ <b>ᴛᴀʀɢᴇᴛ ᴢᴏɴᴇ</b></i> (<code>{to_chat}</code>).
<i>° ɪꜰ ᴛʜᴇ <b>ꜱᴏᴜʀᴄᴇ ᴢᴏɴᴇ</b> ɪꜱ ᴘʀɪᴠᴀᴛᴇ, ᴛʜᴇ ᴜꜱᴇʀʙᴏᴛ ᴍᴜꜱᴛ ʙᴇ ᴘʀᴇꜱᴇɴᴛ ᴛʜᴇʀᴇ.</i>

<b>ɪꜰ ᴀʟʟ ᴄᴏɴᴅɪᴛɪᴏɴꜱ ᴀʀᴇ ᴍᴇᴛ, ᴘʀᴏᴄᴇᴇᴅ ʙʏ ᴄʟɪᴄᴋɪɴɢ ʏᴇꜱ.</b>

<b>⚡ @IND_BOTZ</b>"""
