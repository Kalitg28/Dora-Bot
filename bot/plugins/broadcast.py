from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid
from bot.database import Database

db = Database()

@Client.on_message(filters.command(["broadcast","broadcast@DoraFilterBot"]) & ~filters.channel, group=3)
async def broadcast(bot:Client, update:Message) :

    chat_id = update.chat.id
    chat_type = update.chat.type
    media = False
    markup = False

    if chat_type=="private":
        chat_id = await db.get_conn(chat_id)
        if not chat_id:
            await update.reply_text("Looks Like You Arent Connected To Any Chat To Do A Broadcast")
            return
    
    if not update.reply_to_message:
        await update.reply_text("Please Reply This Command To The Message You Would Like To Broadcast")
        return
    try:
        requester = await bot.get_chat_member(chat_id, update.from_user.id)
        if not requester.status in ("administrator","creator"): return
    except PeerIdInvalid:
        await update.reply_text("Im Not An Admin In Your Group")

    if update.reply_to_message.caption:
        media = True
    if update.reply_to_message.reply_markup:
        markup = update.reply_to_message.reply_markup.inline_keyboard

    async for member in bot.iter_chat_members(chat_id=chat_id):

        id = member.user.id
        try:
         if media :
            if not markup:
                await update.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html"
                )
            else :
                await update.copy(
                    chat_id=id,
                    caption=update.reply_to_message.caption.html,
                    parse_mode="html",
                    reply_markup=InlineKeyboardMarkup(markup)
                )
         else :
            if not markup:
                await update.copy(
                    chat_id=id,
                )
            else :
                await update.copy(
                    chat_id=id,
                    reply_markup=InlineKeyboardMarkup(markup)
                )
        except PeerIdInvalid:
            pass
        except Exception as e:
            print(e)