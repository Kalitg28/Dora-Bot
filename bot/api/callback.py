# (c) @Jisin0
import logging
from time import time
import re

from telegram import Bot, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from .helpers import Helpers
from .multiselect import VERIFY
from .database import Database
from .configs import DICTIONARY, BUTTONS

db = Database()

async def cb_navg(bot:Bot, update: CallbackQuery):
    """
    A Callback Funtion For The Next Button Appearing In Results
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, btn, query = re.findall(r"navigate\((.+)\)", query_data)[0].split("|", 2)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        logging.exception(e)
        ruser_id = None
    
    admin_list = VERIFY.get(str(chat_id))
    if admin_list == None: # Make Admin's ID List
        
        admin_list = []
        
        for x in bot.get_chat_administrators(chat_id=chat_id):
            admin_id = x.user.id 
            admin_list.append(admin_id)
            
        admin_list.append(None) # Just For Anonymous Admin....
        VERIFY[str(chat_id)] = admin_list
    
    if not ((user_id == ruser_id) or (user_id in admin_list)): # Checks if user is same as requested user or is admin
        await update.answer("Nice Try ;)",show_alert=True)
        return


    if btn == "next":
        index_val = int(index_val) + 1
    elif btn == "back":
        index_val = int(index_val) - 1

    FIND = Helpers.read_results_from_file(chat_id, query, index_val)
    if not FIND:
        return await update.answer("Looks Like This Request No LOnger Exists :(")
    temp_results = Helpers.gen_buttons(FIND.get("results"))
    max_pages = FIND.get("max_pages")
    len_results = FIND.get('max_pages')
    print(len_results)
    FIND = {}

    if ((index_val + 1 )== max_pages) or ((index_val + 1) == len_results): # Max Pages

        if not index_val <= 0:
            
            temp_results.append([
            InlineKeyboardButton("⇚ ʙᴀᴄᴋ", callback_data=f"navigate({index_val}|back|{query})")
        ])

    elif int(index_val) <= 0:
        temp_results.append(
                [
                    InlineKeyboardButton(f"📃 ᴘᴀɢᴇ 1/{len_results if len_results < max_pages else max_pages} 📃", callback_data="ignore"),
                    InlineKeyboardButton("ɴᴇxᴛ ⇛", callback_data=f"navigate(0|next|{query})")
                ]
            )

    else:
        temp_results.append([
            InlineKeyboardButton("⇚ ʙᴀᴄᴋ", callback_data=f"navigate({index_val}|back|{query})"),
            InlineKeyboardButton("ɴᴇxᴛ ⇛", callback_data=f"navigate({index_val}|next|{query})")
        ])

    if not int(index_val) == 0:    
        temp_results.append([
            InlineKeyboardButton(f"📃 ᴘᴀɢᴇ {index_val + 1}/{len_results if len_results < max_pages else max_pages} 📃", callback_data="ignore")
        ])

    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ɪɴғᴏ", callback_data="answer(INFO)"), InlineKeyboardButton(f"ᴀʟʟ", callback_data=f"all({query})"), InlineKeyboardButton("sᴇʟᴇᴄᴛ", callback_data=f"multi({index_val}|{query})")]]+temp_results)
    
    try:
        update.message.edit_reply_markup(
                reply_markup=reply_markup
        )
        
    except BadRequest as f:
        logging.exception(f)

async def edit(bot:Bot, update:CallbackQuery):

    update.answer()
    key:str = re.findall(r'edit\((.+)\)', update.data)[0].upper()

    text = DICTIONARY.EN.get(key, "Page Not Defined :(")
    if key=='ABOUT':
        owner = await db.get_bot_setting(bot.id, 'owner')
        text = text.replace('{owner}', str(owner))
    text = text.format(
        mention=update.from_user.mention_html()
    )

    btn = BUTTONS.EN.get(key, BUTTONS.EN['DEFAULT'])

    if update.message.text:
        update.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode='HTML'
        )
    else:
        update.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode='HTML')

async def cb_stats(bot:Bot, update:CallbackQuery):

    stat = await db.get_bot_stats(bot.id)

    text = f"""
U S E R S : {stat['usercount']}
R E Q U E S T S : {stat['requests']}
U P T I M E : {Helpers.humanize_sec(time()-stat['created'])}
A C T I V E : {stat['active']}
"""
    markup = InlineKeyboardMarkup(BUTTONS.EN['STATS'])

    if update.message.text:
        update.edit_message_text(text, reply_markup=markup)
    else:
        update.edit_message_caption(text, reply_markup=markup)