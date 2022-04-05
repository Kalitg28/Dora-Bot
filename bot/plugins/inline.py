from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto, InlineQueryResult
from bot.helpers import Helpers, get_imdb_info
import imdb
from imdb.Movie import Movie
from imdb.Person import Person
import random
from bot.translation import Translation


searcher = imdb.IMDb()

async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query

    results = await all_imdb(text)

    if results:

        await update.answer(
            results=results,
            cache_time=0,
            switch_pm_text=f"Heres What I Found For {text}",
            switch_pm_parameter="start",
            next_offset=""
        )
        
            
    else :

        await update.answer(results=[],
                        cache_time=0,
                        switch_pm_text=f'No Results Were Found For {text}',
                        switch_pm_parameter='idk')

async def all_imdb(query):

     query = query.strip()
     print(query)
     post = False

     if "post:" in query:
         query = query.replace("post:",'')
         post = True

     results = searcher.search_movie(query, results=2)
     Product = []
     try:
          if len(results)<1: return False
          for result in results:

                movie = get_imdb_info(result.movieID, info=Movie.default_info)
                if len(movie)<1: return False

                url = movie.get("full-size cover url", random.choice(Translation.START_PHOTOS))
                caption = f"        <b><u>{movie.get('title', ' ')}</b></u>\n"

                caption+=f"\n🌟 <b>𝚁𝙰𝚃𝙸𝙽𝙶</b> : {movie['rating']}" if movie['rating'] else ''
                caption+=f"\n🗳️ <b>𝚅𝙾𝚃𝙴𝚂</b> : {movie['votes']}" if movie['votes'] else ''
                caption+=f"\n🧬 <b>𝙶𝙴𝙽𝚁𝙴𝚂</b> : {movie['genres']}" if movie['genres'] else ''
                caption+=f"\n⌬ <b>𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴𝚂 :</b> {movie['language']}" if movie['language'] else ''
                caption+=f"\n📅 <b>𝚁𝙴𝙻𝙴𝙰𝚂𝙴𝙳</b> : {movie['released']}" if movie['released'] else ''
                caption+=f"\n⏱️ <b>𝚁𝚄𝙽𝚃𝙸𝙼𝙴</b> : {movie['runtime']}" if movie['runtime'] else ''
                caption+=f"\n⎙ <b>𝙳𝙸𝚁𝙴𝙲𝚃𝙾𝚁 :</b> {movie['director']}" if movie['director'] else ''
                caption+=f"\n⛤ <b>𝙰𝙲𝚃𝙾𝚁𝚂 :</b> {movie['stars']}" if movie['stars'] else ''
                caption+=f"\n🗺️ <b>Storyline</b> : <code>{[movie['plot']]}</code>..." if movie['plot'] else ''
                caption+=f"\n<a href='{movie['link']}'>Read More...</a>"

                if post : caption+="\n\n<b>🅒 Powered By @DM_Linkz</b>"
                
                year = movie.get("year", "")
                
                buttons = [[InlineKeyboardButton("Search Again", switch_inline_query_current_chat=query)],[InlineKeyboardButton("New Search", switch_inline_query_current_chat='')]] if not post else [[InlineKeyboardButton("Join For More..", url="https://t.me/DM_Linkz")]]
                Product.append(InlineQueryResultPhoto(
                    photo_url=url,
                    thumb_url=url,
                    title=movie.get("title","") + f" {year}",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode='html'
                ))
          return Product

     except Exception as e:
         print(e)