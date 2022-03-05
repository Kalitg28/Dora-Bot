import re
import logging
import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait, PhotoIdInvalid, ChatSendMediaForbidden
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, WebpageMediaEmpty

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot
from bot.translation import Translation # pylint: disable=import-error
from bot.helpers import(# pylint: disable=import-error 
Helpers, IMDB
)

from pymongo.cursor import Cursor, CursorType

from .batch import Batch

FIND = {}
INVITE_LINK = {}
ACTIVE_CHATS = {}
db = Database()

@Bot.on_message(filters.text & filters.group & ~filters.bot, group=0)
async def auto_filter(bot:Client, update:Message):
    """
    A Funtion To Handle Incoming Text And Reply With Appropriate Results
    """
    chat_id = update.chat.id

    if chat_id in (-1001547869793,):
        return await update.delete()

    if re.findall(r"((^\/|^,|^\.|^[\U0001F600-\U000E007F]).*)", update.text):
        return
    
    if ("https://" or "http://") in update.text:
        return

    year = re.findall(r"[1-2]\d{3}", update.text) # Targetting Only 1000 - 2999 😁
    if year:
        year = year[0]
    else:
        year = '2022'

    query = update.text.replace(year, '')
    
    if len(query) < 2:
        return
    
    results = []
    
    global ACTIVE_CHATS
    global FIND
    
    configs = await db.find_chat(chat_id)
    achats = ACTIVE_CHATS["902"] if ACTIVE_CHATS.get("902") else await db.find_active(902)
    ACTIVE_CHATS[str(chat_id)] = achats
    
    if not configs:
        return
    movie = await Helpers.cleanse(update.text)
    movie_info = await Helpers.get_movie(movie)
    
    allow_video = True
    allow_audio = False
    allow_document = True
    
    max_pages = configs["configs"]["max_pages"] # maximum page result of a query
    pm_file_chat = configs["configs"]["pm_fchat"] # should file to be send from bot pm to user
    max_results = configs["configs"]["max_results"] # maximum total result of a query
    max_per_page = configs["configs"]["max_per_page"] # maximum buttom per page 
    auto_filter = configs.get('af', True)
    size_button = configs.get('size', False)
    if not auto_filter:
        return
    
    filters = await db.search_media(query, max_results+5)

    if not filters and movie_info:
        
        filters = await db.search_media(movie_info["title"], max_results+5)
    
    if filters:
        all_files = []
        group_text = Batch.encode(str(chat_id))
        for filter in filters: # iterating through each files
            file_name = filter.get("file_name")
            file_type = filter.get("file_type")
            file_link = filter.get("file_link")
            file_size = int(filter.get("file_size", "0"))
            
            # from B to MiB
            
            if file_size < 1024:
                file_size = f"[{file_size} B]"
            elif file_size < (1024**2):
                file_size = f"[{str(round(file_size/1024, 2))} KB]"
            elif file_size < (1024**3):
                file_size = f"[{str(round(file_size/(1024**2), 2))} MB]"
            elif file_size < (1024**4):
                file_size = f"[{str(round(file_size/(1024**3), 2))} GB]"
            
            
            file_size = "" if file_size == ("[0 B]") else file_size
            
            # add emoji down below inside " " if you want..
            
            

            if file_type == "video":
                if allow_video: 
                    pass
                else:
                    continue
                
            elif file_type == "audio":
                if allow_audio:
                    pass
                else:
                    continue
                
            elif file_type == "document":
                if allow_document:
                    pass
                else:
                    continue
            
            if pm_file_chat: 
                unique_id = filter.get("unique_id")
                if not FIND.get("bot_details"):
                    try:
                        bot_= await bot.get_me()
                        FIND["bot_details"] = bot_
                    except FloodWait as e:
                        asyncio.sleep(e.x)
                        bot_= await bot.get_me()
                        FIND["bot_details"] = bot_
                
                bot_ = FIND.get("bot_details")
                file_link = f"https://t.me/{bot_.username}?start=z{unique_id}z{group_text}z"

            if year in file_name:

                if size_button :
                    results+=[[
                        InlineKeyboardButton(file_name, url=file_link),
                        InlineKeyboardButton(file_size, url=file_link)
                    ]]
                
                else:
                    button_text = f"{file_size} {file_name}"
                    results+=[[
                    InlineKeyboardButton(button_text, url=file_link)
                ]]
            
            else:

                if size_button :
                    results.append(
                    [
                        InlineKeyboardButton(file_name, url=file_link),
                        InlineKeyboardButton(file_size, url=file_link)
                    ]
                )
                else:
                    button_text = f"{file_size} {file_name}"
                    results.append(
                [
                    InlineKeyboardButton(button_text, url=file_link)
                ]
            )
            all_files.append(unique_id)
        
    else:

        text = configs.get("noresult", None)
        if not text:
            return

        if text=='def':
            text = f"<b>Sorry I Couldnt Get Any Results For Your Query : <code>{update.text}</code> 😐\n\nClick on The Instructions Below 🙃</b>"
        else :
            text = text.format(mention=(update.from_user.mention if update.from_user else 'User'),
            name=(update.from_user.first_name if update.from_user else 'User'),
            id=(update.from_user.id if update.from_user else 'ID'),
            query=update.text
            )

        await update.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📄 Instructions 📄", callback_data="instruct"), InlineKeyboardButton("🔍 Search 🔎", url=f"https://google.com/search?q={update.text.replace(' ','+')}")]]))

        

        return # return if no files found for that query
    

    if len(results) == 0: # double check
        return
    
    else:
    
        result = []
        # seperating total files into chunks to make as seperate pages
        result += [results[i * max_per_page :(i + 1) * max_per_page ] for i in range((len(results) + max_per_page - 1) // max_per_page )]
        len_result = len(result)
        len_results = len(results)
        results = None # Free Up Memory
        
        FIND[query] = {"results": result, "total_len": len_results, "max_pages": max_pages, "all_files": all_files, "per_page": max_per_page} # TrojanzHex's Idea Of Dicts😅

        # Add next buttin if page count is not equal to 1
        if len_result != 1:
            result[0].append(
                [
                    InlineKeyboardButton(f"📃 Page 1/{len_result if len_result < max_pages else max_pages} 📃", callback_data="ignore"),
                    InlineKeyboardButton("Next ⇛", callback_data=f"navigate(0|next|{query})")
                ]
            )

        results[0]+= [
            InlineKeyboardButton(f"All", callback_data=f"all({query})"),
            InlineKeyboardButton("Select", callback_data=f"multi(0|{query})")
        ]
        
            
        reply_markup = InlineKeyboardMarkup(result[0])

        if not movie_info :

            await update.reply_text(
                text=f"<b>I've Found {len_results} Results For Your Query <code>{update.text}</code></b>",
                reply_markup=reply_markup,
                parse_mode="html"
            )
            return
        elif movie_info["full-size cover url"]=="Unknown":
            await update.reply_text(
                text=f"<b>I've Found {len_results} Results For Your Query <code>{update.text}</code></b>",
                reply_markup=reply_markup,
                parse_mode="html"
            )
            return

        text = f"""
<b>⍞ ᴛɪᴛɪʟᴇ </b>: <code>{movie_info['title']}</code>
<b>⌗ ɢᴇɴʀᴇ </b>: <code>{Helpers.list_to_str(movie_info["genres"])}</code>
<b>★ ʀᴀᴛɪɴɢ </b>: <code>{movie_info["rating"]} / 10</code>
<b>⎚ ᴠᴏᴛᴇs </b>: <code>{movie_info["votes"]} / 10</code>
<b>⌥ ʀᴜɴᴛɪᴍᴇ </b>: <code>{movie_info["runtimes"]}</code>
<b>⌬ ʟᴀɴɢᴜᴀɢᴇs <b>: <code>{Helpers.list_to_str(movie_info['languages'])}</code>
<b>〄 ʀᴇʟᴇᴀꜱᴇ ᴅᴀᴛᴇ</b> : <code>{movie_info["original air date"]}</code>
<b>⎙ ʀᴇsᴜʟᴛs</b> : <code>{len_results}</code>

<i>🅒 Uᴘʟᴏᴀᴅᴇᴅ Bʏ {update.chat.title}</i>
        """

        try:
            await bot.send_photo(
                photo=movie_info["full-size cover url"],
                chat_id = update.chat.id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="html",
                reply_to_message_id=update.message_id
            )

        except MediaEmpty:

            text+=f"<a href='{movie_info['link']}'> </a>"
            await update.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="html"
            )
        
        except WebpageMediaEmpty:

            text+=f"<a href='{movie_info['link']}'> </a>"
            await update.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="html"
            )

        except ChatSendMediaForbidden:
            text+=f"<a href='{movie_info['link']}'> </a>"
            await update.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="html"
            )

        except ButtonDataInvalid:
            print(result[0])
        
        except Exception as e:
            print(e)

        print(update.chat.title)



@Client.on_message(filters.command('search'), group=4)
async def media_search(bot:Client, update:Message):

    query = update.text.split(None, 1)[1]
    await db.search_media(query, 10)


async def gen_invite_links(db, group_id, bot, update):
    """
    A Funtion To Generate Invite Links For All Active 
    Connected Chats In A Group
    """
    chats = db.get("chat_ids")
    global INVITE_LINK
    
    if INVITE_LINK.get(str(group_id)):
        return
    
    Links = []
    if chats:
        for x in chats:
            Name = x["chat_name"]
            
            if Name == None:
                continue
            
            chatId=int(x["chat_id"])
            
            Link = await bot.export_chat_invite_link(chatId)
            Links.append({"chat_id": chatId, "chat_name": Name, "invite_link": Link})

        INVITE_LINK[str(group_id)] = Links
    return 


async def recacher(group_id, ReCacheInvite=True, ReCacheActive=False, bot=Bot, update=Message):
    """
    A Funtion To rechase invite links and active chats of a specific chat
    """
    global INVITE_LINK, ACTIVE_CHATS

    if ReCacheInvite:
        if INVITE_LINK.get(str(group_id)):
            INVITE_LINK.pop(str(group_id))
        
        Links = []
        chats = await db.find_chat(group_id)
        chats = chats["chat_ids"]
        
        if chats:
            for x in chats:
                Name = x["chat_name"]
                chat_id = x["chat_id"]
                if (Name == None or chat_id == None):
                    continue
                
                chat_id = int(chat_id)
                
                Link = await bot.export_chat_invite_link(chat_id)
                Links.append({"chat_id": chat_id, "chat_name": Name, "invite_link": Link})

            INVITE_LINK[str(group_id)] = Links
    
    if ReCacheActive:
        
        if ACTIVE_CHATS.get(str(group_id)):
            ACTIVE_CHATS.pop(str(group_id))
        
        achats = await db.find_active(group_id)
        achatId = []
        if achats:
            for x in achats["chats"]:
                achatId.append(int(x["chat_id"]))
            
            ACTIVE_CHATS[str(group_id)] = achatId
    return 

async def cleanse(query):

    keywords = ["movie", "malayalam", "tamil", "kannada", "hd", "subtitle", "subtitles"]
    query = query.lower()
    for key in keywords:

        if key in query.split():

            query = query.replace(key, '')

    return query

