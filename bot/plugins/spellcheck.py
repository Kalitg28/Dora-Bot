import re
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from pyrogram.types.bots_and_keyboards.callback_query import CallbackQuery
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters

from bot.database import Database 
from bot import VERIFY

db = Database()

@Client.on_message(filters.command("setspell"), group=3)
async def setspell(bot:Client, update:Message):

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
        await update.reply("You Havent Specified A Message Bro")
        return
    caption = extract[1]

    await db.set_main(int(chat_id), "noresult", caption)
    await update.reply("Your Custom Spelling Message Was Saved Successfully...", quote=True)

@Client.on_message(filters.command("delspell"), group=3)
async def delspell(bot:Client, update:Message):

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

    await db.del_main(int(chat_id), "noresult")
    await update.reply("Your Request Was Updated Successfully", quote=True)

@Client.on_callback_query(filters.regex(r'spell\((.+)\)'), group=3)
async def spell_check(bot:Client, update:CallbackQuery):

    action, group_id = re.findall(r'spell\((.+)\)', update.data)[0].split('|',1)
    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)
    buttons = [[
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ]]

    if action=='off':
        await db.del_main(int(group_id), "noresult")
        await update.message.edit("Existing Spelling Message Was Deleted ✅")
        return
    elif action=='on':
        await db.set_main(int(group_id), "noresult", 'def')
        await update.message.edit("Spell Check Was Set To Defaukt Text ... ✅")
        return

    response:Message = await bot.ask(update.message.chat.id, "<b>Now Send Me The New Message You Want Users To See When There's No Results</b>\n\nTo Abort The Process Send /cancel", filters.user(update.from_user.id), timeout=300)
    if not response : return await update.message.reply("Request Timed Out !!",  reply_markup=InlineKeyboardMarkup(buttons))
    if response.text.startswith('/cancel'):
        await update.message.edit('Process SuccessFully Aborted...!!', reply_markup=InlineKeyboardMarkup(buttons))
        return

    await db.set_main(update.message.chat.id, "noresult", response.text)
    await update.message.edit("Your New Spell Check Was Set Successfully... ✅")