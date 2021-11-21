#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG
import re
import random
import asyncio
import threading

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.types.messages_and_media import photo
from pyrogram.types.messages_and_media.message import Message
from bot import Translation, LOGGER # pylint: disable=import-error
from bot.database import Database # pylint: disable=import-error
from bot.plugins.batch import Batch
from bot import Buttons

db = Database()

@Client.on_message(filters.command(["start"]) & filters.private, group=1)
async def start(bot, update):

    add = threading.Thread(target=asyncio.run, args=(db.add_user(update.from_user.id),))
    add.start()
    try:
        file_uid = update.command[1]
    except IndexError:
        file_uid = False

    await bot.send_chat_action(update.chat.id, "typing")
    
    if file_uid:
        if re.findall(r"^a(.+)a(.+)a(.+)", file_uid):
            await Batch.get_batch(file_uid, bot, update)
            await bot.send_chat_action(update.chat.id, "cancel")
            return
        file_id, file_name, file_caption, file_type = await db.get_file(file_uid)
        
        if (file_id or file_type) == None:
            await bot.send_chat_action(update.chat.id, "cancel")
            return
        
        caption = "<b>" + file_name + "</b>"
        try:
            await update.reply_cached_media(
                file_id,
                quote=True,
                caption = caption,
                parse_mode="html",
            )
        except Exception as e:
            await update.reply_text(f"<b>Error:</b>\n<code>{e}</code>", True, parse_mode="html")
            LOGGER(__name__).error(e)
            await bot.send_chat_action(update.chat.id, "cancel")
        return

    buttons = Buttons.EN["START"]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await bot.send_photo(
        photo=random.choice(Translation.START_PHOTOS),
        chat_id=update.chat.id,
        caption=Translation.EN["START"].format(
                update.from_user.mention),
        reply_markup=reply_markup,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )
    await bot.send_chat_action(update.chat.id, "cancel")


@Client.on_message(filters.command(["map"]) & filters.private, group=1)
async def help(bot, update):
    await bot.send_chat_action(update.chat.id, "typing")
    buttons = Buttons.EN["HELP"]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await bot.send_photo(
        photo="https://telegra.ph/file/82b6cf45d478fb5fd33c0.jpg",
        chat_id=update.chat.id,
        caption=Translation.HELP.format(update.from_user.mention),
        reply_markup=reply_markup,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )
    await bot.send_chat_action(update.chat.id, "cancel")


@Client.on_message(filters.command(["about"]) & filters.private, group=1)
async def about(bot, update):

    await bot.send_chat_action(update.message.chat.id, "typing")
    
    buttons = Buttons.EN["ABOUT"]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await bot.send_photo(
        photo=random.choice(Translation.START_PHOTOS),
        chat_id=update.chat.id,
        caption=Translation.ABOUT_TEXT,
        reply_markup=reply_markup,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )
    await bot.send_chat_action(update.chat.id, "cancel")

@Client.on_message(filters.command("id") & filters.incoming, group=1)
async def get_id(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type
    await bot.send_chat_action(update.chat.id, "typing")

    if chat_type=="private":

        if not update.reply_to_message or update.reply_to_message.forward_from_chat:

            await update.reply_text(f"<b>Your ID is : <code>{update.chat.id}</code></b>", parse_mode="html")
            return

        if update.reply_to_message.forward_from_chat.id:

            await update.reply_text(f"<b>This Message Was Forwarded From : <code>{update.reply_to_message.forward_from_chat.id}</code></b>", parse_mode="html")

        else :

            await update.reply_text(f"<b>Your ID is : <code>{update.chat.id}</code></b>", parse_mode="html")

    elif chat_type=="group" or chat_type=="supergroup":

        if update.reply_to_message:

            await update.reply_text(f"This User's ID is : <code>{update.reply_to_message.from_user.id}</code>", parse_mode="html")

        else :

            await update.reply_text(f"This Chat's ID is : <code>{update.chat.id}</code>", parse_mode="html")

    elif chat_type=="channel":

        await update.reply_text(f"This Channel's ID is <code>{update.chat.id}</code>", parse_mode="html")

    await bot.send_chat_action(update.chat.id, "cancel")

@Client.on_message(filters.command("json") & filters.private, group=1)
async def show_json(bot:Client, update:Message):

    await bot.send_chat_action(update.chat.id, "typing")

    if update.reply_to_message:

        message = update.reply_to_message
        message = str(message).replace('"', '').replace(',','</code>,<code>').replace(':', '</code>:<code>')[:4000]

        await update.reply_text(message, parse_mode="html")

    else :

        await update.reply_text(str(update).replace('"', '').replace(',','</code>,<code>').replace(':', '</code>:<code>'), parse_mode="html")

    await bot.send_chat_action(update.chat.id, "cancel")