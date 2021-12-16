import re

from pyrogram.types.bots_and_keyboards.callback_query import CallbackQuery
from pyromod import listen
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatPreview, Chat
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, MessageIdInvalid

from bot.database import Database 
from bot import VERIFY

db = Database()

@Client.on_callback_query(filters.regex(r'fsub\((.+)\)'), group=3)
async def fsub(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'fsub\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)
    buttons = []

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(fsub|off|{group_id})'), InlineKeyboardButton('Change', callback_data=f'fix(fsub|set|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Add New',  callback_data=f'fix(fsub|set|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Change Or Add A Fsub Channel...", reply_markup=InlineKeyboardMarkup(buttons))