from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid, UserIsBot
from bot.database import Database
from bot.translation import Translation

from pymongo.cursor import Cursor

db = Database()
@Client.on_message(filters.command(["broadcast","broadcast@DoraFilterBot"]) & filters.chat(Translation.OWNER_ID), group=3)
async def broadcast_all(bot:Client, update:Message) :

    media = False
    markup = False

    results = await db.all_users()
    count = 0
    status = await bot.send_message(
        chat_id=update.chat.id,
        text="Starting Broadcast...."
    )
    if update.reply_to_message.caption:
        media = True
    if update.reply_to_message.reply_markup:
        markup = InlineKeyboardMarkup(update.reply_to_message.reply_markup.inline_keyboard)
    for result in results:

        id = result["_id"]
        try:
         if media :
            if not markup:
                await update.reply_to_message.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html"
                )
            else :
                await update.reply_to_message.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html",
                    reply_markup=markup
                )
         else :
            if not markup:
                await update.reply_to_message.copy(
                    chat_id=id,
                )
            else :
                await update.reply_to_message.copy(
                    chat_id=id,
                    reply_markup=markup
                )
         count+=1
         await status.edit(f"Broadcasted Successfully To {count} Users")
        except PeerIdInvalid:
            pass
        except Exception as e:
            print(e)

@Client.on_message(filters.command(["broadcast","broadcast@DoraFilterBot"]) & ~filters.channel, group=3)
async def broadcast(bot:Client, update:Message) :

    chat_id = update.chat.id
    chat_type = update.chat.type
    media = False
    markup = False

    if chat_type=="private":
        chat_id = await db.get_conn(chat_id)
        if not chat_id:
            await update.reply_text("Looks Like You Arent Connected To Any Chat To Do A Broadcast", quote=True)
            return
    
    if not update.reply_to_message:
        await update.reply_text("Please Reply This Command To The Message You Would Like To Broadcast", quote=True)
        return
    try:
        requester = await bot.get_chat_member(chat_id, update.from_user.id)
        if not requester.status in ("administrator","creator"): return
    except PeerIdInvalid:
        await update.reply_text("Im Not An Admin In Your Group", quote=True)

    if update.reply_to_message.caption:
        media = True
    if update.reply_to_message.reply_markup:
        markup = update.reply_to_message.reply_markup.inline_keyboard
    count = 0

    status = await bot.send_message(
        chat_id=update.chat.id,
        text="Starting Broadcast...."
    )
    async for member in bot.iter_chat_members(chat_id=chat_id):

        id = member.user.id
        try:
         if media :
            if not markup:
                await update.reply_to_message.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html"
                )
            else :
                await update.reply_to_message.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html",
                    reply_markup=InlineKeyboardMarkup(markup)
                )
         else :
            if not markup:
                await update.reply_to_message.copy(
                    chat_id=id,
                )
            else :
                await update.reply_to_message.copy(
                    chat_id=id,
                    reply_markup=InlineKeyboardMarkup(markup)
                )
         count+=1
         await status.edit(f"Broadcasted Successfully To {count} Users")
        except PeerIdInvalid:
            pass
        except UserIsBot:
            pass
        except Exception as e:
            print(e)