# (c) @MrPurple902

import os

import imdb
import json
import random
import requests

from imdb import Movie
from pyrogram.types import InlineQueryResultPhoto
from pyrogram.types.bots_and_keyboards.inline_keyboard_button import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lxml import html

from bot.translation import Translation


searcher = imdb.IMDb()

class Helpers() :

 
 async def get_movie(my_movie):

    movies = searcher.search_movie(my_movie, results=1)
    if len(movies)<1:
        return False
    try:
       id = movies[0].movieID
    except IndexError:
        return False

    poster = movies[0].get("full-size cover url")

    return get_imdb_info(id), poster

    
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

async def write_results_to_file(chat_id, name:str, data):

    try:
        if not os.path.exists('data/'):
            os.mkdir('data')
        if not os.path.exists(f'data/{chat_id}'):
            os.mkdir(f'data/{chat_id}')

        with open(f'data/{chat_id}/{name}.json','w') as file:
            json.dump(data, file)
        
        return True

    except OSError as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False

async def read_results_from_file(chat_id, name):

    try:
        if not os.path.exists(f'data/{chat_id}/{name}.json'):
            return False

        with open(f'data/{chat_id}/{name}.json', 'r') as file:
            data = json.load(file)

        data['results'] = eval(data['results'])
        data['all_files'] = eval(data['all_files'])
        return data

    except Exception as e:
        print(e)

def href_list_string(items:list()):
    """A Function to convert list elements to string"""

    if len(items) < 1:
        return "Unknown"
    
    string = ''

    for item in items:

        a = item.find('./a')
        href = a.attrib['href']

        string += f"<a href='imdb.com{href}'>{a.text}</a>  "

    return string

def is_available(x):
    """A Proffessional Function to return default if text attrib absent"""

    if x is None:
        return "Unknown"
    return x.text

def get_imdb_info(id):

    """A Function To Scrape The Imdb page of a Movie to get details"""

    title, rating, votes, director, writers, stars, genres, plot, runtime = ("Unknown","Unknown","Unknown","Unknown","Unknown","Unknown","Unknown","Unknown","Unknown")

    try:
        link = f"https://www.imdb.com/title/tt{id}/"
        resp = requests.get(link)
        page = resp.content
        
        print("Fetched webpage successsfully...")
        
        root: html.HtmlElement = html.fromstring(page).body
        main: html.HtmlElement = root.find("./div[2]/main/div/section[1]")
        
        head: html.HtmlElement = main.find("./section/div[3]/section/section")
        title = is_available(head.find("./div[1]/div[1]/h1"))
        title = f"<a href='{link}'>{title}</a>"
        rating = is_available(head.find("./div[1]/div[2]/div/div[@data-testid='hero-rating-bar__aggregate-rating']/a/div/div/div[2]/div[@data-testid='hero-rating-bar__aggregate-rating__score']/span[1]"))
        votes = is_available(head.find("./div[1]/div[2]/div/div[@data-testid='hero-rating-bar__aggregate-rating']/a/div/div/div[2]/div[3]"))
        
        people: html.HtmlElement = head.find("./div[3]/div[2]/div[1]/div[3]/ul")
        director = href_list_string(people.findall("./li[1]/div/ul/li"))
        writers = href_list_string(people.findall("./li[2]/div/ul/li"))
        stars = href_list_string(people.findall("./li[3]/div/ul/li"))
        
        base : html.HtmlElement = main.find("./div/section/div/div[1]")
        
        storyline:html.HtmlElement = base.find("./section[@cel_widget_id='StaticFeature_Storyline']/div[2]")
        genres = href_list_string(storyline.findall("./ul[2]/li[@data-testid='storyline-genres']/div/ul/li"))
        plot = is_available(storyline.find("./div[@data-testid='storyline-plot-summary']/div[1]/div"))
        
        details: html.HtmlElement = base.find("./section[@cel_widget_id='StaticFeature_Details']/div[2]/ul")
        release = href_list_string(details.findall("./li[@data-testid='title-details-releasedate']/div/ul/li"))
        language = href_list_string(details.findall("./li[@data-testid='title-details-languages']/div/ul/li"))
        runtime = base.find("./section[@cel_widget_id='StaticFeature_TechSpecs']/div[2]/ul/li[@data-testid='title-techspec_runtime']/div").text_content()
        
    except Exception as e:
        print(e)

    return dict(
        title=title,
        link=link,
        rating=rating,
        votes=votes,
        director=director,
        writers=writers,
        stars=stars,
        genres=genres,
        plot=plot,
        release=release,
        language=language,
        runtime=runtime
    )
