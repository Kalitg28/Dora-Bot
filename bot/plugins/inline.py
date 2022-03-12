from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto, InlineQueryResult
from bot.helpers import Helpers
import imdb
from imdb.Movie import Movie
from imdb.Person import Person
import random
from bot.translation import Translation


searcher = imdb.IMDb()

@Client.on_inline_query(group=0)
async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query
    print(update)

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

                movie = searcher.get_movie(result.movieID, info=Movie.default_info)
                if len(movie)<1: return False

                url = movie.get("full-size cover url", random.choice(Translation.START_PHOTOS))
                caption = f"        <b><u>{movie.get('title', ' ')}</b></u>\n"

                rating = movie.get("rating", None)
                if rating :
                  caption+=f"\n🌟 <b>Rating</b> : {rating} / 10.0"
               
                votes = movie.get("votes", None)
                if votes:
                   caption+=f"\n🗳️ <b>Votes</b> : {votes}"

                genres = movie.get("genres", None)
                if genres:
                   caption+=f"""\n🧬 <b>Genres</b> : {str(genres).replace('[','').replace(']','').replace("'",'')}"""

                released = movie.get("original air date", None)
                if released:
                    caption+=f"\n📅 <b>Released</b> : {released}"
                else:
                    released = movie.get("year", None)
                    if released:
                        caption+=f"\n📅 <b>Released</b> : {released}"

                duration = movie.get("runtimes", None)
                if duration :
                    try :
                        duration = duration[0]
                        runtime = int(duration)
                        if runtime<60:
                            caption+=f"\n⏱️ <b>Duration</b> : {duration}mins"
                        else:
                            caption+=f"\n⏱️ <b>Duration</b> : {int(runtime/60)}hr {runtime%60}mins"
                    except Exception as e:
                        print(e)

                directors = movie.get("director", None)
                if directors:
                    caption+=f"\n🎩 <b>Director :</b> {directors[0]}"

                plot = movie.get("plot", None)
                if plot:
                    caption+=f"\n\n🗺️ <b>Storyline :</b> <code>{plot[0]}...</code>" 

                caption+=f"\n<a href='https://imdb.com/title/tt/{movie.movieID}'>Read More...</a>"

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