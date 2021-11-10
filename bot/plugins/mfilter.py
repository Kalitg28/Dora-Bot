# (c) @MrPurple902


import re
import logging
import asyncio
import random
import string

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.translation import Translation

db = Database()

class Mfilter():
  def mfilter(text:str, group_id, bot:Client, update:Message):
    '''A Function To Get Manual Filters Of A Chat'''

    query = text
    result = await db.find_mfilter(group_id=group_id, query=query)
    if not result :
        return
    else:
        content, file_id, buttons, sticker = (result["content"], result["file_id"], result["buttons"], result["sticker"])

    content:str = content.format(mention=update.from_user.mention, first_name=update.from_user.first_name, last_name=update.from_user.last_name, full_name=f"{update.from_user.first_name} {update.from_user.last_name}", username=update.from_user.username if update.from_user.username else update.from_user.first_name, id=update.from_user.id)

    if sticker and file_id:
        if buttons:
            await update.reply_sticker(
                sticker=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html"
                )
        else :
            await update.reply_sticker(sticker=file_id)
    elif file_id:
        if buttons:
            await update.reply_cached_media(
                file_id=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
                caption=content
            )
        else:
            await update.reply_cached_media(
                file_id=file_id,
                parse_mode="html",
                caption=content
            )
    else :
        if buttons:
            await update.reply_text(
                text=content,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else :
            await update.reply_text(
                text=content,
                parse_mode="html"
            )

@Client.on_message(filters.command("filter", case_sensitive=False), group=1)
async def n_filter(bot, update: Message):

    chat_id = update.chat.id
    chat_type = update.chat.type
    userid = update.from_user.id
    text = update.text
    sticker = False
    args = update.text.html.split(None, 1)

    if chat_type=="private" :

        chat_id = await db.get_conn(chat_id)

    if not chat_id :

        await update.reply_text("Please Connect To A Chat First To Use This Command In PM")
        return

    st = await bot.get_chat_member(chat_id, userid)
    if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Translation.OWNER_ID)):
        return
        

    if len(args) < 2:
        await update.reply_text("Command Incomplete :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
   
    if not update.reply_to_message and len(extracted) < 2:
        await update.reply_text("Add some content to save your filter!", quote=True)
        return

    try:
                chat = await bot.get_chat(chat_id)
                title = chat.title
    except:
                await update.reply_text("Make sure I'm present in your group!!", quote=True)
                return

    unique_id = ''.join(random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15) )

    if (len(extracted) >= 2) and not update.reply_to_message:
        reply_text, btn, alert = parser(unique_id, "", extracted[1], text)
        fileid = None
        if not reply_text:
            await update.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return
        
    

    elif update.reply_to_message and update.reply_to_message.reply_markup:
        try:
            rm = update.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = update.reply_to_message.document or\
                  update.reply_to_message.video or\
                  update.reply_to_message.photo or\
                  update.reply_to_message.audio or\
                  update.reply_to_message.animation or\
                  update.reply_to_message.sticker
            if update.reply_to_message.sticker:
                sticker = True
            if msg:
                fileid = msg.file_id
                reply_text = update.reply_to_message.caption.html
            else:
                reply_text = update.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]" 
            fileid = None
            alert = None

    elif update.reply_to_message and update.reply_to_message.photo:
        try:
            fileid = update.reply_to_message.photo.file_id
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.caption.html, extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif update.reply_to_message and update.reply_to_message.video:
        try:
            fileid = update.reply_to_message.video.file_id
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.caption.html, extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif update.reply_to_message and update.reply_to_message.audio:
        try:
            fileid = update.reply_to_message.audio.file_id
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.caption.html, extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
   
    elif update.reply_to_message and update.reply_to_message.document:
        try:
            fileid = update.reply_to_message.document.file_id
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.caption.html, extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif update.reply_to_message and update.reply_to_message.animation:
        try:
            fileid = update.reply_to_message.animation.file_id
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.caption.html, extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif update.reply_to_message and update.reply_to_message.sticker:
        try:
            sticker = True
            fileid = update.reply_to_message.sticker.file_id
            reply_text, btn, alert =  parser(unique_id, "", extracted[1], text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    elif update.reply_to_message and update.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(unique_id, update.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None

    else:
        return
    
    await db.add_mfilter(unique_id, chat_id, text, reply_text, fileid, btn, alert, sticker)

    await update.reply_text(
        f"Filter for  `{text}`  added in  **{title}**",
        quote=True,
        parse_mode="md"
    )

@Client.on_message(filters.command("stop", case_sensitive=False), group=1)
async def stop_filter(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM")
        return

    filter = update.text.replace("/stop", '').strip()

    success = await db.del_mfilter(chat_id, filter)

    if success :
        await update.reply_text(f"Successfully Deleted The Filter For {filter}")
    else :
        await update.reply_text(f'Couldnt Delete Any Filter For {filter}')


@Client.on_message(filters.command("filters", case_sensitive=False), group=1)
async def n_filter(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id
    total_filters = ""

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM")
        return

    filters = await db.all_mfilter(chat_id)
    title = await bot.get_chat(chat_id).title
    total_filters = ""
    for filter in filters :
        total_filters+=f"\n- <code>{filter}</code>"

    await update.reply_text(f"Total Of {len(filters)} Manual Filters Have Been Saved For {title} : {total_filters}", parse_mode="html")

def split_quotes(text: str):

    extract = re.findall(r'^("[^"]+")', text)
    if extract :

        return extract[0].replace('"', '').strip(), text.strip('"').strip()

    else :

        split = text.split(' ', 1)

        return split[0], split[1]

def parser(unique_id, reply_text: str, text: str, filter):

    text = reply_text + " \n" + text
    alert_count = 0

    pattern = r"(\[([^\[]+?)\]\((url|alert):(?:/{0,2})(.+?)\))"
    total_buttons = []
    alert = []

    for the_buttons in text.split("\n"):

        line_buttons = []

        for button in re.finditer(pattern, the_buttons):

            text.replace(button, '')

            if button[3]=="url":

                line_buttons.append(InlineKeyboardButton(button[1], url=button[4]))

            elif button[3]=="alert":

                line_buttons.append(InlineKeyboardButton(button[1], callback_data=f"alert({unique_id}|{alert_count})"))
                alert.append(button[3])
                alert_count+=1

        total_buttons.append(line_buttons)

    return text, total_buttons, alert
