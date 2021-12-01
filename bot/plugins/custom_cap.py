import re
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from pyrogram.types.bots_and_keyboards.callback_query import CallbackQuery
from pyrogram.types import Message
from pyrogram import Client, filters

from bot.database import Database 
from bot import VERIFY

db = Database()

@Client.on_message(filters.command("setcaption"), group=3)
async def setcaption(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        print(e)
        return
    
    extract = update.text.split(None, 1)
    if len(extract)<2:
        await update.reply("You Havent Specified A Caption Bro")
        return
    caption = extract[1]

    await db.set_main(int(chat_id), "caption", caption)
    await update.reply("Your Custom Caption Was Saved Successfully...", quote=True)

@Client.on_message(filters.command("delcaption"), group=3)
async def delcaption(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return

    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        print(e)
        return

    await db.del_main(int(chat_id), "caption")
    await update.reply("Your Request Was Updated Successfully", quote=True)