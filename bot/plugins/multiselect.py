import re
import urllib

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot import Translation, Buttons, VERIFY # pylint: disable=import-error
from bot.plugins.auto_filter import ( # pylint: disable=import-error
    FIND, 
    INVITE_LINK, 
    ACTIVE_CHATS
    )
from bot.database import Database # pylint: disable=import-error

SELECTED = {}
db = Database()

@Client.on_callback_query(filters.regex(r'multi\((.+)\)'))
async def multiselect(bot:Client, update:CallbackQuery):

    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, query = re.findall(r"multi\((.+)\)", query_data)[0].split("|", 1)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        print(e)
        ruser_id = None
    
    admin_list = VERIFY.get(str(chat_id))
    if admin_list == None: # Make Admin's ID List
        
        admin_list = []
        
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
            
        admin_list.append(None) # Just For Anonymous Admin....
        VERIFY[str(chat_id)] = admin_list
    
    if not ((user_id == ruser_id) or (user_id in admin_list)): # Checks if user is same as requested user or is admin
        await update.answer("Nice Try :)",show_alert=True)
        return

    res = FIND.get(query).get('results')
    try:
        page = res[int(index_val)].copy()
    except Exception as e:
        print(e)
        return await update.answer("Bad Request :(")

    index = 0
    total_btn = []
    for buttons in page:
        temp = []
        for btn in buttons:
            temp.append(InlineKeyboardButton(btn.text, callback_data=f"sel({index_val}|{index}|{query})"))

        total_btn.append(temp)
        index+=1

    total_btn.append([InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"multi({int(index_val)-1}|{query})"), InlineKeyboardButton("Exɪᴛ", callback_data=f"navigate({int(index_val)+1}|back|{query})"), InlineKeyboardButton("Sᴇɴᴅ", callback_data=f"sensel({query})"), InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"multi({int(index_val)+1}|{query})")])

    await update.message.edit_reply_markup(InlineKeyboardMarkup(total_btn))
    await update.answer()

@Client.on_callback_query(filters.regex(r'^sel\((.+)\)'), group=4)
async def select(bot:Client, update:CallbackQuery):

    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    page, index, query = re.findall(r"sel\((.+)\)", query_data)[0].split("|", 2)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        print(e)
        ruser_id = None
    
    admin_list = VERIFY.get(str(chat_id))
    if admin_list == None: # Make Admin's ID List
        
        admin_list = []
        
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
            
        admin_list.append(None) # Just For Anonymous Admin....
        VERIFY[str(chat_id)] = admin_list
    
    if not ((user_id == ruser_id) or (user_id in admin_list)): # Checks if user is same as requested user or is admin
        await update.answer("Nice Try :)",show_alert=True)
        return

    page_btn = update.message.reply_markup.inline_keyboard
    page_btn[int(index)] = [InlineKeyboardButton('✅', callback_data="answer(SELECTED)")]

    global SELECTED
    prev = SELECTED.get(str(update.from_user.id))
    if not prev:
        SELECTED[str(update.from_user.id)] = {}
        prev = {}
    per_page = FIND.get(query).get('per_page')
    all_files = FIND.get(query).get('all_files')
    file_index = per_page * int(page) + int(index)
    unique_id = all_files[file_index]

    if prev.get(query):
        prev[query].append(unique_id)
    else:
        prev[query] = [unique_id]

    SELECTED[str(update.from_user.id)] = prev

    await update.message.edit_reply_markup(InlineKeyboardMarkup(page_btn))
    await update.answer()

@Client.on_callback_query(filters.regex(r'sensel\((.+)\)'), group=4)
async def sensel(bot:Client, update:CallbackQuery):

    chat_id = update.message.chat.id
    user_id = update.from_user.id

    settings = await db.find_chat(chat_id)
    fsub = settings.get("fsub", None)
        

    if fsub:
                fsub = fsub["id"]
                try:
                    member = await bot.get_chat_member(int(fsub), user_id)
                    if member.status=='kicked':
                        await update.answer("Sorry Dude You're Banned In My Force Subscribe Channel So You Cant Use Me Right Now.....!!", show_alert=True)
                        return
                except PeerIdInvalid:
                    pass
                except UserNotParticipant:
                    chat = str(chat_id).replace('-100','').replace('-','')
                    return await update.answer(url=f"https://t.me/DoraFilterBot?start=fsubz{fsub}a{chat}a{update.message.message_id}z")

    global SELECTED

    if not SELECTED.get(str(user_id)):
        return await update.answer("Tʜɪs Bᴜᴛᴛᴏɴ Isɴᴛ Fᴏʀ Yᴏᴜ :(", show_alert=True)

    query = re.findall(r"sensel\((.+)\)", update.data)[0]

    if not SELECTED[str(user_id)].get(query):
        return await update.answer("Tʜɪs Bᴜᴛᴛᴏɴ Isɴᴛ Fᴏʀ Yᴏᴜ :(", show_alert=True)

    files = SELECTED[str(user_id)][query]

    for file in files:

            file_id, file_name, file_caption, file_type = await db.get_file(file)
            file_caption = "<b>" + file_name + "</b>\n\n" + settings.get("caption", "")
            try:
                await bot.send_cached_media(
                user_id,
                file_id,
                caption = file_caption,
                parse_mode="html",
            )
            except PeerIdInvalid:
                chat = str(chat_id).replace('-100','').replace('-','')
                return await update.answer(url=f"https://t.me/DoraFilterBot?start=retryz{chat}a{update.message.message_id}z")
            except UserIsBlocked:
                chat = str(chat_id).replace('-100','').replace('-','')
                url=f"https://t.me/DoraFilterBot?start=retryz{chat}a{update.message.message_id}z"
                return await update.answer(url)
            except Exception as e:
                print(e)
                return await update.answer(f"Error:\n{e}", show_alert=True)

    await update.answer("Fɪʟᴇs Hᴀᴠᴇ Bᴇᴇɴ Sᴇɴᴛ Tᴏ PM :)", show_alert=True)