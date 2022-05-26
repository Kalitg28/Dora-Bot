# (c) @Jisin0

import re

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid, UserIsBot, UserIsBlocked
from bot.database import Database
from bot.translation import Translation

db = Database()

async def connected_cast(bot:Client, update:Message) :

    caption = None
    markup = None

    results = await db.all_connected()
    count = 0
    block = 0
    err=0
    status = await bot.send_message(
        chat_id=update.chat.id,
        text="Starting Broadcast...."
    )
    if update.reply_to_message.caption:
        caption = update.reply_to_message.caption.html
    if update.reply_to_message.reply_markup:
        markup = InlineKeyboardMarkup(update.reply_to_message.reply_markup.inline_keyboard)
    for result in results:

        id = result["_id"]
        try:
            sent = await update.reply_to_message.copy(
                    chat_id=id,
                    caption=caption,
                    parse_mode="html",
                    reply_markup=markup
                )

            count+=1
            await status.edit(f"Current broadcast stats:\nSuccess: {count}\nBlocked: {block}\nError: {err}")
            await bot.send_message(Translation.OWNER_ID, sent.chat.title)
        except PeerIdInvalid:
            err+=1
        except UserIsBlocked:
            block+=1
        except Exception as e:
            print(e)
            err+=1

async def broadcast_all(bot:Client, update:Message) :

    caption = None
    markup = None

    results = await db.all_users()
    count = 0
    block = 0
    err=0
    status = await bot.send_message(
        chat_id=update.chat.id,
        text="Starting Broadcast...."
    )
    if update.reply_to_message.caption:
        caption = update.reply_to_message.caption.html
    if update.reply_to_message.reply_markup:
        markup = InlineKeyboardMarkup(update.reply_to_message.reply_markup.inline_keyboard)
    for result in results:

        id = result["_id"]
        try:
            sent = await update.reply_to_message.copy(
                    chat_id=id,
                    caption=caption,
                    parse_mode="html",
                    reply_markup=markup
                )

            count+=1
            await status.edit(f"Current broadcast stats:\nSuccess: {count}\nBlocked: {block}\nError: {err}")
            await bot.send_message(Translation.OWNER_ID, sent.chat.title)
        except PeerIdInvalid:
            err+=1
        except UserIsBlocked:
            block+=1
        except Exception as e:
            print(e)
            err+=1

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

        await status.edit(f"Completed Broadcast Successfully To {count} Users")

def parser(text):

    pattern = r"(\[([^\[]+?)\]\((url|search):(?:/{0,2})(.+?)\))"
    total_buttons = []

    for the_buttons in text.split("\n"):

        line_buttons = []

        for button in re.finditer(pattern, the_buttons):

            text = text.replace(button[1], '')

            if button[3]=="url":

                line_buttons.append(InlineKeyboardButton(button[2], url=button[4]))
                
            elif button[3]=="search":

                line_buttons.append(InlineKeyboardButton(button[2], switch_inline_query_current_chat=button[4]))

        if len(line_buttons)>0:
            total_buttons.append(line_buttons)

    if len(total_buttons)<1:
        total_buttons = False
    return text, total_buttons