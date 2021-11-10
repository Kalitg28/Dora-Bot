import re
import logging
import asyncio
import random
import threading

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import ButtonDataInvalid, FloodWait, PhotoIdInvalid

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot
from bot.translation import Translation # pylint: disable=import-error

from bot.helpers import(# pylint: disable=import-error 
Helpers, IMDB
)

from .mfilter import Mfilter

FIND = {}
INVITE_LINK = {}
ACTIVE_CHATS = {}
db = Database()

@Bot.on_message(filters.text & filters.incoming & ~filters.bot, group=0)
async def auto_filter(bot, update:Message):
    """
    A Funtion To Handle Incoming Text And Reply With Appropriate Results
    """
    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        if not chat_id:
            return
        await Mfilter.mfilter(text=update.text, group_id=chat_id, bot=bot, update=update)
        return

    mfilter = await threading.Thread(target=Mfilter.mfilter, args=(update.text, chat_id, bot, update))
    await mfilter.start()

    if re.findall(r"((^\/|^,|^\.|^[\U0001F600-\U000E007F]).*)", update.text):
        return
    
    if ("https://" or "http://") in update.text:
        return
    
    query = re.sub(r"[1-2]\d{3}", "", update.text) # Targetting Only 1000 - 2999 😁
    
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
    movie = await cleanse(update.text)
    imdb = threading.Thread(target=Helpers.get_movie, args=(movie,))
    await imdb.start()
    
    allow_video = True
    allow_audio = False
    allow_document = True
    
    max_pages = configs["configs"]["max_pages"] # maximum page result of a query
    pm_file_chat = configs["configs"]["pm_fchat"] # should file to be send from bot pm to user
    max_results = configs["configs"]["max_results"] # maximum total result of a query
    max_per_page = configs["configs"]["max_per_page"] # maximum buttom per page 
    
    filters = await db.get_filters(902, query)
    
    if filters:
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
            button_text = f"{file_size}{file_name.replace(' ', '.')}"
            

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
            
            if len(results) >= max_results:
                break
            
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
                file_link = f"https://t.me/{bot_.username}?start={unique_id}"
            
            results.append(
                [
                    InlineKeyboardButton(button_text, url=file_link)
                ]
            )
        
    else:
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
        
        FIND[query] = {"results": result, "total_len": len_results, "max_pages": max_pages} # TrojanzHex's Idea Of Dicts😅

        # Add next buttin if page count is not equal to 1
        if len_result != 1:
            result[0].append(
                [
                    InlineKeyboardButton(f"📃 Page 1/{len_result if len_result < max_pages else max_pages} 📃", callback_data="ignore"),
                    InlineKeyboardButton("Next ⇛", callback_data=f"navigate(0|next|{query})")
                ]
            )
        
            
        reply_markup = InlineKeyboardMarkup(result[0])

        imdb.join()

        movie_info = IMDB.get(movie)

        if not movie_info: return print("You Idiot This Doesnt Work") 


        text = f'''
        📽️ Movie/Series : {query}
        🌟 Rating : {movie_info["rating"]}
        🗳️ Votes : {movie_info["votes"]}
        🧬 Genres : {movie_info["genres"]}
        📅 Released : {movie_info["original air date"]}
        ⏱️ Duration : {movie_info["runtimes"]}
        📁 Results : {(len_results)}

        🅒 Uploaded By  {update.chat.title}
        '''

        try:
            await bot.send_photo(
                photo=movie_info["full-size cover url"],
                chat_id = update.chat.id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="html",
                reply_to_message_id=update.message_id
            )

        except PhotoIdInvalid:

            await bot.reply_photo(
                photo = random.choice(Translation.PHOTO_LIST)
            )

        except ButtonDataInvalid:
            print(result[0])
        
        except Exception as e:
            print(e)

        return



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

