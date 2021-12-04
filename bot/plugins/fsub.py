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

    action, group_id = re.findall(r'fsub\((.+)\)', update.data)[0].split('|',1)
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
        await db.del_fsub(int(group_id))
        await update.message.edit("Existing Fsub Channel Was Deleted ✅")
        return

    response:Message = await bot.ask(update.message.chat.id, "Ok Now Send ONLY THE ID Of The Force Sub Channel And Make Sure I'm An Admin There Too \n\nTo See The ID Go To The Channel And Send <code>/id</code>\n\nTo Abort The Process Send /cancel", filters.user(update.from_user.id), timeout=300)
    if not response : return await update.message.reply("Request Timed Out !!",  reply_markup=InlineKeyboardMarkup(buttons))
    if response.text.startswith('/cancel'):
        await update.message.edit('Process SuccessFully Aborted...!!', reply_markup=InlineKeyboardMarkup(buttons))
        return

    try :
        group_id = int(group_id)
        id = int(response.text)
        channel:Chat = await bot.get_chat(id)
        if not channel.invite_link : return await update.message.edit("I Dont Have Enough Permissions In The Fsub Channel", reply_markup=InlineKeyboardMarkup(buttons))

        await db.set_fsub(group_id, id, channel.title)
        await update.message.edit("Fsub Channel Was Set Successfully...!!", reply_markup=InlineKeyboardMarkup(buttons))

    except PeerIdInvalid:
        await update.message.edit("Looks Like Im Not Member Of A Channel with This ID", reply_markup=InlineKeyboardMarkup(buttons))
        return
    except TypeError:
        await update.message.edit("Thats Not A Valid Chat ID...", reply_markup=InlineKeyboardMarkup(buttons))
        return
    except Exception as e :
        print(e)
        await update.message.edit("Something Went Terribly Wrong....!!", reply_markup=InlineKeyboardMarkup(buttons))
        return