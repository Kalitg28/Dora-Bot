#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG
import re
import random
import asyncio
import threading

from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.types.messages_and_media import photo
from pyrogram.types.messages_and_media.message import Message
from pyrogram.raw.functions.messages import GetAllChats
from bot import Translation, LOGGER # pylint: disable=import-error
from bot.database import Database # pylint: disable=import-error
from bot.plugins.batch import Batch
from bot import Buttons

db = Database()

@Client.on_message(filters.command('test') & filters.chat(Translation.OWNER_ID))
async def test(bot, update):
    res = await bot.send(GetAllChats(except_ids=[]))
    print(res)
    print(str(res))
    
@Client.on_message(filters.command(["start"]) & filters.private, group=4)
async def start(bot:Client , update):

    add = threading.Thread(target=asyncio.run, args=(db.add_user(update.from_user.id),))
    add.start()
    try:
        file_uid:str = update.command[1]
    except IndexError:
        file_uid = False

    await bot.send_chat_action(update.chat.id, "typing")
    
    if file_uid:
        if file_uid.startswith('fsub'):
            try:
                id, link = re.findall(r'fsub\((.+)\)', file_uid)[0].split('|', 1)
                chat = await bot.get_chat(int(id))
                buttons = [[InlineKeyboardButton("Join 🤓", url=link),InlineKeyboardButton("Retry ♻️", url=f"https://t.me/DoraFilterBot?start={file_uid}")]]
                await update.reply(
                text="<b>Sorry Man You'll Have To Join My Channel First To Use Me 🙂🙂\n\nJust Click On The Join Button Below And Come Back And Click On Retry......</b>",
                quote=True,
                reply_markup=InlineKeyboardMarkup(buttons)
                    )
            except Exception as e:
                print(e)
                await update.reply_text(f"Try Contacting Support Group Reason : <code>{e}</code>", parse_mode='html')
        elif file_uid.startswith('retry'):
            link = file_uid.strip('retry')
            return await update.reply_text("Now Please Return And Try Again :)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", url=link)]]))
        elif file_uid.startswith('connect'):
            try:
                chat_id = int(file_uid.strip('connect '))
                try:
                    member = await bot.get_chat_member(chat_id, update.chat.id)
                    if not member.status in ('creator','administrator'):
                        return update.reply_text("You Dont Have Permission For That Bro :(")
                    result = await db.conn_user(update.from_user.id, chat_id)
                    if result :
                        return await update.reply_text("I've Successfully Connected You With And Can Do Any CHanges From Here :)") 
                    else:
                        return await update.reply_text("Connection Failed Try Contacting Support :(")
                except PeerIdInvalid:
                    return await update.reply_text("Looks Like Im Not Member Of That Chat Or The URl Is Invalid :(")
            except:
                return await update.reply_text("Thats An Invalid URL")

        if re.findall(r"^a(.+)a(.+)a(.+)", file_uid):
            await Batch.get_batch(file_uid, bot, update)
            await bot.send_chat_action(update.chat.id, "cancel")
            return

        results = re.findall(r"^z(.+)z(.+)z$", file_uid)[0]
        if len(results)<2: return await update.reply_text("Thats Not A Valid Url Man...!", quote=True)
        new_uid = results[0]
        group_id = Batch.decode(results[1])
        settings = await db.find_chat(int(group_id))
        fsub = settings.get("fsub", None)
        

        if fsub:
                    fsub = fsub["id"]
                    fsub_msg = settings.get('fsub_msg')
                    try:
                        member = await bot.get_chat_member(int(fsub), update.from_user.id)
                        if member.status=='kicked':
                            await update.reply("Sorry Dude You're Banned In My Force Subscribe Channel So You Cant Use Me Right Now.....!!", quote=True)
                            return
                    except PeerIdInvalid:
                        pass
                    except TypeError as e:
                        print(e)
                        await update.reply_text("Thats Not A Valid Url Man...!", quote=True)
                        return
                    except UserNotParticipant:
                        chat = await bot.get_chat(int(fsub))
                        link = chat.invite_link
                        if not fsub_msg:
                            buttons = [[InlineKeyboardButton("Join 🤓", url=link),InlineKeyboardButton("Retry ♻️", url=f"https://t.me/DoraFilterBot?start={file_uid}")]]
                            await update.reply(
                            text="<b>Sorry Man You'll Have To Join My Channel First To Use Me 🙂🙂\n\nJust Click On The Join Button Below And Come Back And Click On Retry......</b>",
                            quote=True,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                        else:
                            buttons = [[InlineKeyboardButton("Join 🤓", url=link),InlineKeyboardButton("Retry ♻️", url=f"https://t.me/DoraFilterBot?start={file_uid}")]]
                            await update.reply(
                            text=fsub_msg,
                            quote=True,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                        return
                    except Exception as e:
                        print(e)

        caption = settings.get("caption", '')
        file_id, file_name, file_caption, file_type = await db.get_file(new_uid)
        
        if (file_id or file_type) == None:
            return
        
        file_caption = "<b>" + file_name + "</b>\n\n" + caption
        try:
            await update.reply_cached_media(
                file_id,
                quote=True,
                caption = file_caption,
                parse_mode="html",
            )
        except Exception as e:
            await update.reply_text(f"<b>Error:</b>\n<code>{e}</code>", True, parse_mode="html")
            LOGGER(__name__).error(e)
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


@Client.on_message(filters.command(["map"]) & filters.private, group=4)
async def help(bot, update):
    await bot.send_chat_action(update.chat.id, "typing")
    buttons = Buttons.EN["HELP"]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await bot.send_photo(
        photo="https://telegra.ph/file/82b6cf45d478fb5fd33c0.jpg",
        chat_id=update.chat.id,
        caption=Translation.EN["HELP"].format(update.from_user.mention),
        reply_markup=reply_markup,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )
    await bot.send_chat_action(update.chat.id, "cancel")


@Client.on_message(filters.command(["about"]) & filters.private, group=4)
async def about(bot, update):

    await bot.send_chat_action(update.chat.id, "typing")
    
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

@Client.on_message(filters.command(["id","id@DoraFilterBot"]) & filters.incoming, group=4)
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

@Client.on_message(filters.command("json","json@DoraFilterBot") & filters.incoming, group=4)
async def show_json(bot:Client, update:Message):

    await bot.send_chat_action(update.chat.id, "typing")

    if update.reply_to_message:

        message = update.reply_to_message
        message = str(message).replace('"', '').replace(',','</code>,<code>').replace(':', '</code>:<code>')[:4000]

        await update.reply_text(message, parse_mode="html")

    else :

        await update.reply_text(str(update).replace('"', '').replace(',','</code>,<code>').replace(':', '</code>:<code>'), parse_mode="html")

    await bot.send_chat_action(update.chat.id, "cancel")

@Client.on_message(filters.command(["stats", "stats@DoraFilterBot"]), group=4)
async def cb_stats(bot:Client, update):

    try:

        stats = await db.get_stats()
        await update.reply_text(
            f"Files : {stats['files']}\n\nUsers : {stats['users']}\n\nConnected Users : {stats['conn']}\n\nManual Filters : {stats['filters']}\n\nCustomized Chats : {stats['chats']}\n\nSpace Used : {stats['used']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✘ Close ✘", callback_data="close")]])
        )
    except Exception as e:
        print(e)
