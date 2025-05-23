import random
import string
import asyncio
import re

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated, InputMediaPhoto
from pyrogram.errors import UserAlreadyParticipant, FloodWait, UserNotParticipant, PeerIdInvalid
from pyrogram.methods.messages.delete_messages import DeleteMessages
from pyrogram.types.messages_and_media.message import Message
from pyrogram.raw.functions.messages import GetAllChats

from bot import VERIFY # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.database import Database # pylint: disable=import-error
from bot.plugins.auto_filter import recacher # pylint: disable=import-error
from bot import Translation
from bot.helpers import Helpers

db = Database()
    
    
async def connect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /add Command TO COnnect A Chat With Group
    """
    chat_id = 902
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("Invalid Username...!!!")
                return
            target = target_chat[1]
            
        elif not target_chat[1].startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("Invalid Chat Id...\nChat ID Should Be Something Like This: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Invalid Input...\nYou Should Specify Valid <code>chat_id(-100xxxxxxxxxx)</code> or <code>@username</code>")
        return
    
    try:
        join_link = await bot.export_chat_invite_link(target)
    except Exception as e:
        print(e)
        await update.reply_text(f"Make Sure Im Admin At <code>{target}</code> And Have Permission For '<i>Inviting Users via Link</i>' And Try Again.....!!!")
        return
    
    userbot_info = await bot.USER.get_me()
    userbot_id = userbot_info.id
    userbot_name = userbot_info.first_name
    
    #try:
    #    await bot.USER.join_chat(join_link)
        
    #except UserAlreadyParticipant:
    #    pass
    
    #except Exception:
    #    await update.reply_text(f"My UserBot [{userbot_name}](tg://user?id={userbot_id}) Couldnt Join The Channel `{target}` Make Sure Userbot Is Not Banned There Or Add It Manually And Try Again....!!")
    #   return
    
    try:
        c_chat = await bot.get_chat(target)
        channel_id = c_chat.id
        channel_name = c_chat.title
        
    except Exception as e:
        await update.reply_text("Encountered Some Issue..Please Check Logs..!!")
        raise e
        
        
    in_db = await db.in_db(chat_id, channel_id)
    
    if in_db:
        await update.reply_text("Channel Aldready In Db...!!!")
        return
    
    wait_msg = await update.reply_text("Please Wait Till I Add All Your Files From Channel To Db\n\n<i>This May Take 10 or 15 Mins Depending On Your No. Of Files In Channel.....</i>\n\nUntil Then Please Dont Sent Any Other Command Or This Operation May Be Intrupted....")
    
    try:
        type_list = ["video", "audio", "document"]
        data = []
        skipCT = 0
        count = 0

        for typ in type_list:

            async for msgs in bot.USER.search_messages(channel_id,filter=typ): #Thanks To @PrgOfficial For Suggesting
                
                # Using 'if elif' instead of 'or' to determine 'file_type'
                # Better Way? Make A PR
                try:
                    if msgs.video:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.video.file_id
                        file_name = msgs.video.file_name[0:-4]
                        file_size = msgs.video.file_size
                        file_type = "video"
                    
                    elif msgs.audio:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.audio.file_id
                        file_name = msgs.audio.file_name[0:-4]
                        file_size = msgs.audio.file_size
                        file_type = "audio"
                    
                    elif msgs.document:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(str(e))
                            continue
                        file_id = file_id.document.file_id
                        file_name = msgs.document.file_name[0:-4]
                        file_size = msgs.document.file_size
                        file_type = "document"
                    
                    for i in ["_", "|", "-", "."]: # Work Around
                        try:
                            file_name = file_name.replace(i, " ")
                        except Exception:
                            pass
                    
                    file_link = msgs.link
                    group_id = chat_id
                    unique_id = ''.join(
                        random.choice(
                            string.ascii_lowercase + 
                            string.ascii_uppercase + 
                            string.digits
                        ) for _ in range(15)
                    )
                    
                    dicted = dict(
                        file_id=file_id, # Done
                        unique_id=unique_id,
                        file_name=file_name,
                        file_caption="",
                        file_size=file_size,
                        file_type=file_type,
                        file_link=file_link,
                        chat_id=channel_id,
                        group_id=group_id,
                    )
                    
                    data.append(dicted)
                    count+=1
                    await wait_msg.edit_text(f"Fetched Data Of {count} Files")
                except Exception as e:
                    if 'NoneType' in str(e): # For Some Unknown Reason Some File Names are NoneType
                        skipCT +=1
                        continue
                    print(e)

        print(f"{skipCT} Files Been Skipped Due To File Name Been None..... #BlameTG")
    except Exception as e:
        await wait_msg.edit_text("Couldnt Fetch Files From Channel... Please look Into Logs For More Details")
        raise e
    
    await db.add_filters(data)
    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text(f"Channel Was Sucessfully Added With <code>{len(data)}</code> Files..")


async def disconnect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /del Command TO Disconnect A Chat With A Group
    """
    chat_id = 902
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    
    try:
        target = int(target_chat[1])
    except TypeError:
        target = target_chat[1]
    except Exception as e:
        print(e)
    
    userbot = await bot.USER.get_me()
    userbot_name = userbot.first_name
    userbot_id = userbot.id
    
    try:
        channel_info = await bot.USER.get_chat(target)
        channel_id = channel_info.id
    except Exception:
        await update.reply_text(f"My UserBot [{userbot_name}](tg://user?id={userbot_id}) Couldnt Fetch Details Of `{target}` Make Sure Userbot Is Not Banned There Or Add It Manually And Try Again....!!")
        return
    
    in_db = await db.in_db(chat_id, channel_id)
    
    if not in_db:
        await update.reply_text("This Channel Is Not Connected With The Group...")
        return
    
    wait_msg = await update.reply_text("Deleting All Files Of This Channel From DB....!!!\n\nPlease Be Patience...Dont Sent Another Command Until This Process Finishes..")
    
    await db.del_filters(chat_id, channel_id)
    await db.del_active(chat_id, channel_id)
    await db.del_chat(chat_id, channel_id)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text("Sucessfully Deleted All Files From DB....")


async def delall(bot: Bot, update):
    """
    A Funtion To Handle Incoming /delall Command TO Disconnect All Chats From A Group
    """
    chat_id=902
    
    await db.delete_all(chat_id)
    await recacher(chat_id, True, True, bot, update)
    
    await update.reply_text("Sucessfully Deleted All Connected Chats From This Group....")

async def new_in_channel(bot:Client, update:ChatMemberUpdated):

    member = update.new_chat_member
    if not member:
        return
    await bot.send_message(-1001547869793, f"Hey {member.user.mention} You Can Post The Movie Files For Me Here :)")
    if update.invite_link:
        await bot.revoke_chat_invite_link(update.invite_link)

async def new_files(bot: Bot, update:Message):
    """
    A Funtion To Handle Incoming New Files In A Channel ANd Add Them To Respective Channels..
    """
    channel_id = update.chat.id
    
    # Using 'if elif' instead of 'or' to determine 'file_type'
    # Better Way? Make A PR
    
    try:
        if update.video: 
            file_type = "video" 
            file_id = update.video.file_id
            file_name = update.video.file_name[0:-4]
            file_size = update.video.file_size

        elif update.audio:
            file_type = "audio"
            file_id = update.audio.file_id
            file_name = update.audio.file_name[0:-4]
            file_size = update.audio.file_size

        elif update.document:
            file_type = "document"
            file_id = update.document.file_id
            file_name = update.document.file_name[0:-4]
            file_size = update.document.file_size

        for i in ["_", "|", "-", "."]: # Work Around
            try:
                file_name = file_name.replace(i, " ")
            except Exception:
                pass
    except Exception as e:
        print(e)
        print(f"WTF : {e}")
        return
        
    
    file_link = update.link
    unique_id = ''.join(
        random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15)
    )
    
    data = []


    data_packets = dict(
                    file_id=file_id, # File Id For Future Updates Maybe...
                    unique_id=unique_id,
                    file_name=file_name,
                    file_caption="",
                    file_size = file_size,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=902,
                )
            
    data.append(data_packets)

    await db.add_filters_reverse(data)
    print('added')
    return

async def del_filter(bot:Client, update):

    try:

        link = update.link
        print(link)
        if not link:
            print("No Attrib Link")
            return

        await db.del_filter(link)
        
    except Exception as e:
        print(e)

async def del_file(bot:Client, update:Message):

    if not update.from_user.id==Translation.OWNER_ID:
        return
    else:
        msg = update.reply_to_message
        hm = await db.del_file(msg.document.file_id)
        if hm:
            await msg.delete()
            await update.delete()
            await update.reply_text(f"File {msg.document.file_name} was Removed From Database Successfully :)")

async def close_trigger(bot:Client, update:Message):

    cmd, type, chat_id, message_id, text = update.text.split(' ', 4)

    reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Rᴇᴀᴅ ᴍᴏʀᴇ", callback_data="answer(CLOSED)")
            ]])

    if type=="photo":

        path = await Helpers.gen_closed_img(text)
        await bot.edit_message_media(
            chat_id=int(chat_id),
            message_id=int(message_id),
            media=InputMediaPhoto(
                media=path,
                caption=f"<i>Tʜᴇ Rᴇsᴜʟᴛs Fᴏʀ {text} Wᴀs Cʟᴏsᴇᴅ Aғᴛᴇʀ Tɪᴍᴇᴏᴜᴛ</i>",
                parse_mode='html'
            ),
            reply_markup=reply_markup
        )
    elif type=="text":

        await bot.edit_message_text(
            chat_id=int(chat_id),
            message_id=int(message_id),
            caption=f"<i>Tʜᴇ Rᴇsᴜʟᴛs Fᴏʀ {text} Wᴀs Cʟᴏsᴇᴅ Aғᴛᴇʀ Tɪᴍᴇᴏᴜᴛ</i>",
            parse_mode='html',
            reply_markup=reply_markup
        )