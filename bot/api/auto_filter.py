import logging
import re
import asyncio

from telegram import Bot, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from .helpers import Helpers, write_imdb_results
from .database import Database

db = Database()

async def auto_filter(bot:Bot, update:Message):
    """
    A Funtion To Handle Incoming Text And Reply With Appropriate Results
    """
    chat_id = update.chat.id

    if chat_id in (-1001547869793,):
        return update.delete()

    if re.findall(r"((^\/|^,|^\.|^[\U0001F600-\U000E007F]).*)", update.text):
        return
    
    if ("https://" or "http://") in update.text :
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
    
    configs = await db.get_config(chat_id)
    
    if not configs:
        return
    movie = await Helpers.cleanse(update.text)
    movie_info, poster = await Helpers.get_movie(movie)
    
    max_pages = configs["configs"]["max_pages"] # maximum page result of a query
    max_results = configs["configs"]["max_results"] # maximum total result of a query
    max_per_page = configs["configs"]["max_per_page"] # maximum buttom per page 
    auto_filter = configs.get('af', True)

    if not auto_filter:
        return
    
    filters = await db.search_media(query, max_results+5)

    if not filters and movie_info:
        
        filters = await db.search_media(movie_info["title"], max_results+5)

    settings = await db.get_autofilter_settings(bot.id)

    button_template = settings.get('btemp', "『 {file_size} 』 {file_name}")
    
    if filters:
        all_files = []
        group_text = Helpers.encode(str(chat_id))
        for filter in filters: # iterating through each files
            file_name = filter.get("file_name")
            file_link = filter.get("file_link")
            file_size = int(filter.get("file_size", "0"))
            
            # from B to MiB
            
            if file_size < 1024:
                file_size = f"{file_size} B]"
            elif file_size < (1024**2):
                file_size = f"{str(round(file_size/1024, 2))} KB"
            elif file_size < (1024**3):
                file_size = f"{str(round(file_size/(1024**2), 2))} MB"
            elif file_size < (1024**4):
                file_size = f"{str(round(file_size/(1024**3), 2))} GB"
            
            
            file_size = "" if file_size == ("0 B") else file_size

            unique_id = filter.get("unique_id")

            file_link = f"https://t.me/{bot.username}?start=z{unique_id}z{group_text}z"

            button_text = button_template.format(
                    file_size=file_size,
                    file_name=file_name
                )

            if year in file_name:
                results = [{'name': button_text, 'url': file_link}] + results
            
            else:
                results.append({'name': button_text, 'url': file_link})
            all_files.append(unique_id)
        
    else:

        text = configs.get("noresult", None)
        if not text:
            return

        if text=='def':
            text = f"<b>Sorry I Couldnt Get Any Results For Your Query : <code>{update.text}</code> 😐\n\nClick on The Instructions Below 🙃</b>"
        else :
            text = text.format(mention=(update.from_user.mention_html() if update.from_user else 'User'),
            name=(update.from_user.first_name if update.from_user else 'User'),
            id=(update.from_user.id if update.from_user else 'ID'),
            query=update.text
            )

        update.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📄 Instructions 📄", callback_data="instruct"), InlineKeyboardButton("🔍 Search 🔎", url=f"https://google.com/search?q={update.text.replace(' ','+')}")]]), parse_mode='html')

        

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
        
        data = {"results": result, "total_len": len_results, "max_pages": max_pages, "all_files": all_files, "per_page": max_per_page} # TrojanzHex's Idea Of Dicts😅
        sucess = await Helpers.write_results_to_file(chat_id, query, data)
        if not sucess:
            print(f"Faled To Write Data Of Query {query} To FIle...")
            
        reply_markup = [[
            InlineKeyboardButton("ɪɴғᴏ", callback_data="answer(INFO)"),
            InlineKeyboardButton(f"ᴀʟʟ", callback_data=f"all({query})"),
            InlineKeyboardButton("sᴇʟᴇᴄᴛ", callback_data=f"multi(0|{query})")
        ]]+ Helpers.gen_buttons(result[0])

        # Add next buttin if page count is not equal to 1
        if len_result != 1:
            reply_markup.append(
                [
                    InlineKeyboardButton(f"📃 ᴘᴀɢᴇ 1/{len_result if len_result < max_pages else max_pages} 📃", callback_data="ignore"),
                    InlineKeyboardButton("ɴᴇxᴛ ⇛", callback_data=f"navigate(0|next|{query})")
                ]
            )

        reply_markup = InlineKeyboardMarkup(reply_markup)
        msg = False

        if not movie_info :

            result_template = settings.get('result_template', "<b>I'ᴠᴇ Fᴏᴜɴᴅ {len_results} Rᴇsᴜʟᴛs Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ <code>{update.text}</code></b>")

            text = result_template.format(
                len_results=len_results,
                query=query,
                first_name=update.from_user.first_name,
                last_name=update.from_user.last_name,
                full_name=update.from_user.full_name,
                user_id=update.from_user.id,
                mention=update.from_user.mention_html()
            )

            msg = update.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

        elif not poster:
            msg = update.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

        if movie_info:

            try:

                text = """
<b>⍞ 𝚃𝙸𝚃𝙻𝙴 :</b> {title}
<b>★ 𝚁𝙰𝚃𝙸𝙽𝙶 :</b> <i>{rating} / 10</i>
<b>⎚ 𝚅𝙾𝚃𝙴𝚂 :</b> <i>{votes}</i>
<b>⌗ 𝙶𝙴𝙽𝚁𝙴𝚂 :</b> <i>{genres}</i>
<b>⌥ 𝚁𝚄𝙽𝚃𝙸𝙼𝙴 :</b> <i>{runtime}</i>
<b>⌬ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴𝚂 :</b> <i>{language}</i>
<b>〄 𝚁𝙴𝙻𝙴𝙰𝚂𝙴𝙳 :</b> <i>{release}</i>
<b>⎙ 𝙳𝙸𝚁𝙴𝙲𝚃𝙾𝚁 :</b> <i>{director}</i>
<b>⛤ 𝙰𝙲𝚃𝙾𝚁𝚂 :</b> <i>{stars}</i>

""".format(
    title=movie_info['title'],
    rating=movie_info['rating'],
    votes=movie_info['votes'],
    genres=movie_info['genres'],
    director=movie_info['director'],
    writers=movie_info['writers'],
    stars=movie_info['stars'],
    release=movie_info['release'],
    plot=movie_info['plot'],
    language=movie_info['language'],
    runtime=movie_info['runtime']
)
                text+=f"<i>🅒 ᑌᑭᏞᝪᗩᗞᗴᗞ ᗷᎩ: {update.chat.title}</i>"

                msg = bot.send_photo(
                    photo=poster,
                    chat_id = update.chat.id,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                    reply_to_message_id=update.message_id
                )

                await write_imdb_results(movie_info['id'], movie_info)
                await db.finished_request(bot.id)
            except Exception as e:
                logging.exception(e)