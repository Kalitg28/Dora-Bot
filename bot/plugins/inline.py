from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto, InlineQueryResult
from bot.helpers import Helpers
import imdb
from imdb.Movie import Movie
import random
from bot.translation import Translation


searcher = imdb.IMDb()

@Client.on_inline_query()
async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query
    print(update)

    results = await all_imdb(text)

    if len(results)<1:
        await update.answer(results=[],
                        cache_time=0,
                        switch_pm_text=f'No Results Were Found For {text}',
                        switch_pm_parameter='idk')
            
    else :

        await update.answer(
            results=results,
            cache_time=0,
            switch_pm_text=f"Heres What I Found For {text}",
            switch_pm_parameter="start",
            next_offset=""
        )

async def all_imdb(query):

     query = query.strip()
     print(query)

     results = searcher.search_movie(query, results=10)
     Product = []
     try:
          if len(results)<1: return False
          for result in results:

                movie = searcher.get_movie(result.movieID, info=Movie.Movie.default_info)
                if len(movie)<1: return False

                url = movie.get("full-size cover url", random.choice(Translation.START_PHOTOS))
                caption = ""

                rating = movie.get("rating", None)
                if rating :
                  caption+=f"🌟 <b>Rating</b> : {rating}"
               
                votes = movie.get("votes", None)
                if votes:
                   caption+=f"🗳️ <b>Votes</b> : {votes}"

                genres = movie.get("genres", None)
                if genres:
                   caption+=f"🧬 <b>Genres</b> : {genres}"

                released = movie.get("original air date", None)
                if released:
                    caption+=f"📅 <b>Released</b> : {released}"
                else:
                    released = movie.get("year", None)
                    if released:
                        caption+=f"📅 <b>Released</b> : {released}"

                duration = movie.get("runtimes", None)
                if duration :
                    try :
                        duration = duration[0]
                        runtime = int(duration)
                        if runtime<60:
                            caption+=f"⏱️ <b>Duration</b> : {duration}mins"
                        else:
                            caption+=f"⏱️ <b>Duration</b> : {runtime/60}hr {runtime%60}mins"
                    except Exception as e:
                        print(e)

                plot = movie.get("plot", None)
                if plot:
                    caption+=f"🗺️ Storyline : {plot[0]}"
                
                year = movie.get("year", "")
                
                buttons = [[InlineKeyboardButton("Search Again", switch_inline_query_current_chat=query)],[InlineKeyboardButton("New Search", switch_inline_query_current_chat='')]]
                Product.append(InlineQueryResultPhoto(
                    photo_url=url,
                    thumb_url=url,
                    title=movie.get("localized title","") + f" {year}",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                ))

     except Exception as e:
         print(e)