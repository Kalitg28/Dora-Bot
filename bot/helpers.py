# (c) @MrPurple902

import imdb
import random
from imdb import Movie
from pyrogram.types import InlineQueryResultPhoto
from pyrogram.types.bots_and_keyboards.inline_keyboard_button import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from bot.translation import Translation


searcher = imdb.IMDb()

class Helpers() :

 
 async def get_movie(my_movie):

    info = ["title", "rating", "votes", "genres", "runtimes", "original air date", "languages", "full-size cover url", "kind", "localized title"]
    movies = searcher.search_movie(my_movie, results=1)
    if len(movies)<1:
        return False
    try:
       movie_id = movies[0].movieID
    except IndexError:
        return False

    movie: Movie = searcher.get_movie(movie_id, info=Movie.Movie.default_info)

    movie_info = {}

    for key in info :

        try :

            movie_info[key] = movie.get(key)
            if not movie_info[key]:
                movie_info[key] = "Unknown"

        except Exception as e :

            print(e)

    movie_info['id'] = movie_id
    movie_info['link'] = f"https://imdb.com/title/tt{movie_id}"
    movie_info['rating_link'] = f"https://imdb.com/title/tt{movie_id}/ratings"
    movie_info['release_link'] = f"https://imdb.com/title/tt{movie_id}/releaseinfo"

    air_date = movie.get("original air date", None)
    if not air_date:

        movie_info["originl air date"] = movie.get("year")
    

    try :

        runtime = int(movie_info["runtimes"][0])

        if runtime>=60:
            
            movie_info["runtimes"] = f"{int(runtime/60)}hr {runtime%60}mins"

        else :

            movie_info.pop("runtimes")
            movie_info["runtimes"] = f"{runtime} mins"
        link = f"https://imdb.com/title/tt{movie.movieID}"
        movie_info['link'] = link

    except Exception as e:
        print(e)
        return False

    return movie_info

 async def cleanse(query:str):

    keywords = ["movie", "malayalam", "tamil", "kannada", "hd", "subtitle", "subtitles"]
    query = query.lower()
    for key in keywords:

        if key in query.split():

            query = query.replace(key, '')

    return query

 async def all_imdb(query):

     print(query)
     post = False
     query2 = query.query
     if "post:" in query.query: 
         query2 = query2.replace("post:",'') 
         post = True
     results = searcher.search_movie(query2, results=5)
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

                released = movie.get("released", None)
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
                    caption+=f"🗺️ <b>Storyline</b> : <code>{plot[0]}</code>..."

                caption+=f"<a href='https://imdb.com/title/tt/{movie.movieID}'>Read More...</a>"

                if post : caption+="\n\nBy @DM_Linkz"
                
                year = movie.get("year", "")
                
                
                buttons = [[InlineKeyboardButton("Search Again", switch_inline_query_current_chat=query)],[InlineKeyboardButton("New Search", switch_inline_query_current_chat='')]] if not post else [[InlineKeyboardButton("Join For More..", url="https://t.me/DM_Linkz")]]
                Product.append(InlineQueryResultPhoto(
                    photo_url=url,
                    thumb_url=url,
                    title=movie.get("title","") + f" {year}",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                ))

     except Exception as e:
         print(e)

 async def list_to_str(l):

     if type(l)=="str":
         return l
     res = " ".join(l)
     return res

 
 async def gen_closed_img(text):

    # Open an Image
    W, H = (640, 640)
    img = Image.new("RGBA",(W,H),"black")
    overlay = Image.open('/app/bot/assets/closed2.png')

    # Call draw Method to add 2D graphics in an image
    I1 = ImageDraw.Draw(img)

    # Custom font style and font size
    myFont = ImageFont.truetype('/app/bot/assets/Meteora.ttf', int((W/len(text)*2)-(275/len(text))))

    w, h = I1.textsize(text, myFont)
    print(w, h)

    # Add Text to an image
    I1.text(text=text, font=myFont, fill =(300, 1000, 1000), xy=((W/2)-(w/2) + 10, H/2-(h/2)), align='center')

    #Pasting overlas to image
    img.paste(overlay, (20,75), mask=overlay)

    path = f'/app/bot/assets/{text}.png'
    img.save(path)

    return path