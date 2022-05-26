import telegram
import logging
import re

from telegram import Bot, CallbackQuery, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Unauthorized

from .database import Database
from .helpers import Helpers
from .clonecmd import DORA
SELECTED = {}
VERIFY = {}
db = Database()


async def multiselect(bot:Bot, update:CallbackQuery):

    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, query = re.findall(r"multi\((.+)\)", query_data)[0].split("|", 1)
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
        update.answer("Nice Try :)",show_alert=True)
        return

    res = Helpers.read_results_from_file(chat_id, query, int(index_val))
    if not res:
        return update.answer("Looks Like This Request No LOnger Exists :(")
    page = res['results']
    print(page)

    index = 0
    total_btn = []
    for p in page:
        print(p)
        total_btn.append([InlineKeyboardButton(p['name'], callback_data=f"sel({index_val}|{index}|{query})")])
        index+=1

    total_btn.append([InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"multi({int(index_val)-1}|{query})"), InlineKeyboardButton("Exɪᴛ", callback_data=f"navigate({int(index_val)+1}|back|{query})"), InlineKeyboardButton("Sᴇɴᴅ", callback_data=f"sensel({query})"), InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"multi({int(index_val)+1}|{query})")])

    update.message.edit_reply_markup(InlineKeyboardMarkup(total_btn))
    update.answer()
    res = []

async def select(bot:Bot, update:CallbackQuery):

    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    page, index, query = re.findall(r"sel\((.+)\)", query_data)[0].split("|", 2)
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
        update.answer("Nice Try :)",show_alert=True)
        return

    page_btn = update.message.reply_markup.inline_keyboard
    page_btn[int(index)] = [InlineKeyboardButton('✅', callback_data="answer(SELECTED)")]

    global SELECTED
    prev = SELECTED.get(str(update.from_user.id))
    if not prev:
        SELECTED[str(update.from_user.id)] = {}
        prev = {}
    FIND = Helpers.read_results_from_file(chat_id, query)
    if not FIND:
        return update.answer("Looks Like This Request No LOnger Exists :(")

    per_page = FIND.get('per_page')
    all_files = FIND.get('all_files')
    file_index = per_page * int(page) + int(index)
    unique_id = all_files[file_index]

    if prev.get(query):
        prev[query].append(unique_id)
    else:
        prev[query] = [unique_id]

    SELECTED[str(update.from_user.id)] = prev

    update.message.edit_reply_markup(InlineKeyboardMarkup(page_btn))
    update.answer()
    FIND = {}


async def sensel(bot:Bot, update:CallbackQuery):

    chat_id = update.message.chat.id
    user_id = update.from_user.id

    settings = await db.get_config(chat_id)
    fsub = settings.get("fsub", None)
        

    if fsub:
                fsub = fsub["id"]
                try:
                    member = bot.get_chat_member(int(fsub), user_id)
                except BadRequest:
                    url=f"https://t.me/{bot.username}?start=fsub{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                    print(url)
                    return update.answer(url=url.replace('-100',''))

    global SELECTED

    if not SELECTED.get(str(user_id)):
        return update.answer("Tʜɪs Bᴜᴛᴛᴏɴ Isɴᴛ Fᴏʀ Yᴏᴜ :(", show_alert=True)

    query = re.findall(r"sensel\((.+)\)", update.data)[0]

    if not SELECTED[str(user_id)].get(query):
        return update.answer("Tʜɪs Bᴜᴛᴛᴏɴ Isɴᴛ Fᴏʀ Yᴏᴜ :(", show_alert=True)

    files = SELECTED[str(user_id)][query]

    for file in files:

            file_id, file_name, file_caption, file_type = await db.get_file(file)
            file_caption = "<b>" + file_name + "</b>\n\n" + settings.get("caption", "")
            try:
                DORA.send_document(
                user_id,
                file_id,
                caption = file_caption,
                parse_mode="HTML",
            )
            except BadRequest:
                url=f"https://t.me/{bot.username}?start=retryz{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                print(url)
                return update.answer(url=url.replace('-100',''))
            except Unauthorized:
                url=f"https://t.me/{bot.username}?start=retryz{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                print(url)
                return update.answer(url=url.replace('-100',''))
            except Exception as e:
                logging.exception(e)
                return update.answer(f"Error:\n{e}", show_alert=True)

    update.answer("Fɪʟᴇs Hᴀᴠᴇ Bᴇᴇɴ Sᴇɴᴛ Tᴏ PM :)", show_alert=True)


async def cb_all(bot:Bot, update:CallbackQuery):

    chat_id = update.message.chat.id
    try:
        query = re.findall(r"all\((.+)\)", update.data)[0]
        FIND = Helpers.read_results_from_file(chat_id, query)
        if not FIND:
            return update.answer("Looks Like This Request No LOnger Exists :(")

        all_files = FIND.get("all_files")
        settings = await db.get_config(chat_id)
        fsub = settings.get("fsub", None)

        if fsub:
                fsub = fsub["id"]
                try:
                    member:ChatMember = await bot.get_chat_member(int(fsub), update.from_user.id)
                    if member.status=='kicked':
                        update.answer("Sorry Dude You're Banned In My Force Subscribe Channel So You Cant Use Me Right Now.....!!", show_alert=True)
                        return
                except BadRequest:
                    url=f"https://t.me/{bot.username}?start=fsub{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                    print(url)
                    return update.answer(url=url.replace('-100',''))

        for file in all_files:

            file_id, file_name, file_caption, file_type = await db.get_file(file)
            file_caption = "<b>" + file_name + "</b>\n\n" + settings.get("caption", "")
            try:
                DORA.send_document(
                update.from_user.id,
                file_id,
                caption = file_caption,
                parse_mode="HTML",
            )
            except BadRequest:
                url=f"https://t.me/{bot.username}?start=retryz{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                print(url)
                return update.answer(url=url.replace('-100',''))
            except Unauthorized:
                url=f"https://t.me/{bot.username}?start=retryz{str(chat_id).replace('-100','').strip()}a{update.message.message_id}z"
                print(url)
                return update.answer(url=url.replace('-100',''))
            except Exception as e:
                update.answer(f"Error:\n{e}", show_alert=True)
                logging.exception(e)
                return

        update.answer("Fɪʟᴇs Hᴀᴠᴇ Bᴇᴇɴ Sᴇɴᴛ Tᴏ PM :)", show_alert=True)
        FIND = {}
        all_files = []

    except Exception as e:
        logging.exception(e)