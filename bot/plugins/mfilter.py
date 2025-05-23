# (c) @MrPurple902


import re
import logging
import asyncio
import random
import string
import pyrogram

from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.translation import Translation

db = Database()



async def new_filter(bot, update: Message):

    chat_id = update.chat.id
    chat_type = update.chat.type
    userid = update.from_user.id
    text = update.text
    sticker = False
    args = update.text.html.split(None, 1)

    if chat_type=="private" :

        chat_id = await db.get_conn(userid)
        print("Mark 1")

        if not chat_id :

            await update.reply_text("Please Connect To A Chat First To Use This Command In PM", quote=True)
            return
    if not chat_id==902:
        st = await bot.get_chat_member(chat_id, userid)

        print("Mark 2")
        if not ((st.status == "administrator") or (st.status == "creator") or (userid in (Translation.OWNER_ID,))):
            return
        

    if len(args) < 2:
        await update.reply_text("Command Incomplete :(", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()

    print("Mark 3")
   
    if not update.reply_to_message and len(extracted) < 2:
        await update.reply_text("Add some content to save your filter!", quote=True)
        return

    try:
                chat = await bot.get_chat(chat_id)
                title = chat.title
    except :
                if not chat_id==902:
                    title = 'Global'
                    await update.reply_text("Make sure I'm present in your group!!", quote=True)
                    return
                title = 'Global'


    unique_id = ''.join(random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15) )
    edits = {}

    if (len(extracted) >= 2) and not update.reply_to_message:
        reply_text, btn, alert, edits = parser(unique_id, "", extracted[1])
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
            btn = False 
            fileid = None
            alert = None

    elif update.reply_to_message and update.reply_to_message.photo:
        try:
            fileid = update.reply_to_message.photo.file_id
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.caption.html, extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None

    elif update.reply_to_message and update.reply_to_message.video:
        try:
            fileid = update.reply_to_message.video.file_id
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.caption.html, extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None

    elif update.reply_to_message and update.reply_to_message.audio:
        try:
            fileid = update.reply_to_message.audio.file_id
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.caption.html, extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None
   
    elif update.reply_to_message and update.reply_to_message.document:
        try:
            fileid = update.reply_to_message.document.file_id
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.caption.html, extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None

    elif update.reply_to_message and update.reply_to_message.animation:
        try:
            fileid = update.reply_to_message.animation.file_id
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.caption.html, extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None

    elif update.reply_to_message and update.reply_to_message.sticker:
        try:
            sticker = True
            fileid = update.reply_to_message.sticker.file_id
            reply_text, btn, alert, edits =  parser(unique_id, "", extracted[1])
        except:
            reply_text = ""
            btn = False
            alert = None

    elif update.reply_to_message and update.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert, edits = parser(unique_id, update.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = False
            alert = None

    else:
        return
    
    await db.add_mfilter(unique_id, chat_id, text, reply_text.replace('"',''), fileid, str(btn), alert, sticker, edits)

    await update.reply_text(
        f"Successfully Saved A Manual Filter For `{text}` in **{title}**",
        quote=True,
        parse_mode="md"
    )

async def stop_filter(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM", quote=True)
        return

    filter = update.text.split(" ", 1)[1]

    success = await db.del_mfilter(chat_id, filter)

    if success :
        await update.reply_text(f"Successfully Deleted The Filter For {filter}", quote=True)
    else :
        await update.reply_text(f'Couldnt Delete Any Filter For {filter}', quote=True)


async def n_filter(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id
    total_filters = ""

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM", quote=True)
        return

    filters = await db.all_mfilter(chat_id)
    try:
        chat = await bot.get_chat(chat_id)
        title = chat.title
    except Exception:
        title = 'Global'
    total_filters = ""
    if not filters :
        await update.reply_text("Looks Like You Havent Saved Any Filters In This Chat", quote=True)
        return
    for filter in filters :
        total_filters+=f"\n- <code>{filter}</code>"

    await update.reply_text(f"Total Of {len(filters)} Manual Filters Have Been Saved For {title} : {total_filters}", parse_mode="html", quote=True)

def split_quotes(text: str):

    extract = re.findall(r'^("([^"]+)")', text)
    if extract :

        return extract[0][1], text.replace(extract[0][1],'')

    else :

        split = text.split(None, 1)
        if len(split)>1:
            return [split[0], split[1]]
        else:
            return [split[0],""]

def parser(unique_id, reply_text: str, text: str):

    text = reply_text + " \n" + text
    alert_count = 0
    edit_count = 0
    processed_list = []

    if "(edit:" in text:
        control = text
        
        while "(edit:" in chunk:
            index = control.index("(edit:")+6
            control = control[index:]
            chunk = control
            bracks = 1
            end_index = index

            for chr in chunk:

                if bracks<1:
                    break
            
                if chr=='(':
                    bracks+=1
                elif chr==')':
                    bracks-=1
                end_index+=1
        
            processed = chunk[index:end_index-1]
            text = text.replace(processed,'def')
            processed_list.append(processed)
            control = control.replace(processed, '')



    pattern = r"(\[([^\[]+?)\]\((buttonurl|url|alert|search|inline|google|edit|home):(?:/{0,2})(.+?)\))"
    total_buttons = []
    alert = []
    edits = []

    for the_buttons in text.split("\n"):

        line_buttons = []

        for button in re.finditer(pattern, the_buttons):

            text = text.replace(button[1], '')

            if button[3]=="url" or button[3]=="buttonurl":

                line_buttons.append(InlineKeyboardButton(button[2], url=button[4]))

            elif button[3]=="alert":

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"alert({unique_id}|{alert_count})"))
                alert.append(button[4])
                alert_count+=1

            elif button[3]=="search":

                line_buttons.append(InlineKeyboardButton(button[2], switch_inline_query_current_chat=button[4]))

            elif button[3]=="inline":

                line_buttons.append(InlineKeyboardButton(button[2], switch_inline_query=button[4]))

            elif button[3]=="google":

                line_buttons.append(InlineKeyboardButton(button[2], url=f"google.com/search?q={button[4].replace(' ','+')}"))

            elif button[3]=="edit":

                text2, total_buttons2, alert2 = edit_parser(
                    unique_id=unique_id,
                    text=processed_list[edit_count],
                    alert_count=alert_count,
                    edit_count=edit_count
                )
                edits.append(dict(
                    text=text2,
                    buttons=total_buttons2
                ))
                alert += alert2

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"edit_t({unique_id}|{edit_count})"))
                edit_count += 1

            elif button[3]=='home':

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"edit_m({unique_id})"))

                

        if len(line_buttons)>0:
            total_buttons.append(line_buttons)

    if len(total_buttons)<1:
        total_buttons = False
    return text, total_buttons, alert, edits

def edit_parser(unique_id, text: str, alert_count, edit_count):

    
    alert_count2 = 0
    edit_count2 = 0

    pattern = r"(\[([^\[]+?)\]\((buttonurl|url|alert|search|inline|google|edit|home):(?:/{0,2})(.+?)\))"
    total_buttons = []
    alert = []

    for the_buttons in text.split("\n"):

        line_buttons = []

        for button in re.finditer(pattern, the_buttons, flags=re.IGNORECASE):

            text = text.replace(button[1], '')

            if button[3]=="url" or button[3]=="buttonurl":

                line_buttons.append(InlineKeyboardButton(button[2], url=button[4]))

            elif button[3]=="alert":

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"alert({unique_id}|{alert_count+alert_count2})"))
                alert.append(button[4])
                alert_count2+=1

            elif button[3]=="search":

                line_buttons.append(InlineKeyboardButton(button[2], switch_inline_query_current_chat=button[4]))

            elif button[3]=="inline":

                line_buttons.append(InlineKeyboardButton(button[2], switch_inline_query=button[4]))

            elif button[3]=="google":

                line_buttons.append(InlineKeyboardButton(button[2], url=f"google.com/search?q={button[4].replace(' ','+')}"))

            elif button[3]=='home':

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"edit_m({unique_id})"))

            elif button[3]=='home':

                line_buttons.append(InlineKeyboardButton(button[2], callback_data=f"edit_m({unique_id})"))
                
        if len(line_buttons)>0:
            total_buttons.append(line_buttons)

    if len(total_buttons)<1:
        total_buttons = False
    else:
        total_buttons = str(total_buttons)
    return text, total_buttons, alert