# (c) @MrPurple902

from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.translation import Translation

db = Database()

@Client.on_message(filters.text & (filters.private | filters.group) & ~filters.bot & ~filters.edited, group=1)
async def mfilter(bot:Client, update:Message):
    '''A Function To Get Manual Filters Of A Chat'''

    chat_type = update.chat.type
    chat_id = update.chat.id
    buttons = False

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        if not chat_id:
            return


    query = update.text
    result = await db.find_mfilter(group_id=chat_id, query=query)
    if not result :
        return
    else:
        content, file_id, btn, sticker = (result["content"], result["file_id"], result["buttons"], result["sticker"])
    if btn:
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

