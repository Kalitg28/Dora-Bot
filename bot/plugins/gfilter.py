import re
import logging
import asyncio
import random
import string
import pyrogram

from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.translation import Translation

db = Database()

@Bot.on_message(filters.text & filters.group & ~filters.bot, group=2)
async def global_filter(bot, update:Message):

    configs = await db.find_chat(update.chat.id)

    g_filter = configs.get('global', True)
    if not g_filter: return

    f_result = await db.find_mfilter(group_id=902, query=update.text)
    if not f_result :
        return
    else:
        content, file_id, btn, sticker = (f_result["content"], f_result["file_id"], f_result["buttons"], f_result["sticker"])
    if btn:
        print(btn)
        buttons = eval(btn)

    content:str = content.format(mention=update.from_user.mention, first_name=update.from_user.first_name, last_name=update.from_user.last_name, full_name=f"{update.from_user.first_name} {update.from_user.last_name}", username=update.from_user.username if update.from_user.username else update.from_user.first_name, id=update.from_user.id)

    if sticker and file_id:
        if buttons:
            await update.reply_sticker(
                sticker=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
                )
        else :
            await update.reply_sticker(sticker=file_id)
    elif file_id:
        if buttons:
            await update.reply_cached_media(
                file_id=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
                caption=content,
                quote=True
            )
        else:
            await update.reply_cached_media(
                file_id=file_id,
                parse_mode="html",
                caption=content,
                quote=True
            )
    else :
        if buttons:
            await update.reply_text(
                text=content,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
        else :
            await update.reply_text(
                text=content,
                parse_mode="html",
                quote=True
            )

