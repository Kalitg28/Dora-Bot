# (c) @Jisin0

import logging
import os

import json
import urllib3
import aiohttp
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from lxml import html

class Helpers() :

 
 async def get_movie(my_movie):

    movies = await search_imdb(my_movie, max=1)
    if not movies:
        return False, False
    id = movies[0]['id']
    print(id)
    try:
        poster = movies[0]['i']['imageUrl']
    except:
        poster=False
    return (await get_imdb_info(id), poster)

    
 async def cleanse(query:str):

    keywords = ["movie", "malayalam", "tamil", "kannada", "hd", "subtitle", "subtitles"]
    query = query.lower()
    for key in keywords:

        if key in query.split():

            query = query.replace(key, '')

    return query

 async def all_imdb(query):

    try:
        query = query.strip()
        print(query)
        post = False      
        if "post:" in query:
            query = query.replace("post:",'')
            post = True      
        results = await search_imdb(query, 3)
        Product = []
    
        if len(results)<=0: 
            return False
        for result in results:
              movie = await get_imdb_info(result['id'], False)
              url = result['i'].get("imageUrl", "https://static.turbosquid.com/Preview/2020/08/18__04_34_57/Still_1.jpgC9E5FEBE-F1D6-43A0-AAAF-75B860A036D3Large.jpg")
              caption = f"        <b><u>{movie.get('title', ' ')}</u></b>\n"
              caption+=f"\n<b>𝚁𝙰𝚃𝙸𝙽𝙶</b> : {movie['rating']}" if movie['rating'] else ''
              caption+=f"\n<b>𝚅𝙾𝚃𝙴𝚂</b> : {movie['votes']}" if movie['votes'] else ''
              caption+=f"\n<b>𝙶𝙴𝙽𝚁𝙴𝚂</b> : {movie['genres']}" if movie['genres'] else ''
              caption+=f"\n<b>𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴𝚂 :</b> {movie['language']}" if movie['language'] else ''
              caption+=f"\n<b>𝚁𝙴𝙻𝙴𝙰𝚂𝙴𝙳</b> : {movie['release']}" if movie['release'] else ''
              caption+=f"\n<b>𝚁𝚄𝙽𝚃𝙸𝙼𝙴</b> : {movie['runtime']}" if movie['runtime'] else ''
              caption+=f"\n<b>𝙳𝙸𝚁𝙴𝙲𝚃𝙾𝚁 :</b> {movie['director']}" if movie['director'] else ''
              caption+=f"\n<b>𝙰𝙲𝚃𝙾𝚁𝚂 :</b> {movie['stars']}" if movie['stars'] else ''
              caption+=f"\n<b>Storyline</b> : <code>{movie['plot']}</code>..." if movie['plot'] else ''
              caption = caption[:1000] +f"\n<a href='{movie['link']}'>Read More...</a>"
              if post : caption+="\n\n<b>🅒 Powered By @DM_Linkz</b>"
              
              year = movie.get("year", "")
              
              buttons = [[InlineKeyboardButton("Search Again", switch_inline_query_current_chat=query)],[InlineKeyboardButton("New Search", switch_inline_query_current_chat='')]] if not post else [[InlineKeyboardButton("Join For More..", url="https://t.me/DM_Linkz")]]
              Product.append(InlineQueryResultPhoto(
                  photo_url=url,
                  thumb_url=url,
                  title=movie.get("rawtitle","") + f" {year}",
                  caption=caption,
                  reply_markup=InlineKeyboardMarkup(buttons),
                  parse_mode='html'
              ))
        return Product
    except Exception as e:
        logging.exception(e)
        return False

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
 def encode(text:str):
        string = text
        encoder = {'1': 'B', '2':'Y', '3':'i', '4':'P', '5':'q', '6':'k', '7':'r', '8':'R', '9':'J', '0':'h', ' ':'a', '-': 'u'}

        for key in encoder.keys():
            string = string.replace(key, encoder[key])

        return string.strip()

 def decode(text:str):

        string = text
        decoder = {'B':'1', 'Y':'2',  'i':'3', 'P':'4', 'q':'5', 'k':'6', 'r':'7', 'R':'8', 'J':'9', 'h':'0', 'a':' ', 'u': '-'}

        for key in decoder.keys():
            string = string.replace(key, decoder[key])
    
        return string.strip()

 async def write_results_to_file(chat_id, name:str, data:dict):

    try:
        if not os.path.exists('./botdata/'):
            os.mkdir('./botdata')
        if not os.path.exists(f'./botdata/{chat_id}'):
            os.mkdir(f'./botdata/{chat_id}')

        with open(f'./botdata/{chat_id}/{name}.json','w') as file:
            file.write(str(data))
        
        return True

    except OSError as e:
        logging.exception(e)
        return False
    except Exception as e:
        logging.exception(e)
        return False

 def read_results_from_file(chat_id, name, index=0):

    try:
        if not os.path.exists(f'./botdata/{chat_id}/{name}.json'):
            return False

        with open(f'./botdata/{chat_id}/{name}.json', 'r') as file:
            data = eval(file.read())

        outdata = dict(
            results=data['results'][index],
            total_len=data['total_len'],
            max_pages=data['max_pages'],
            per_page=data['per_page'],
            all_files=data['all_files']
        )
        print(outdata)
        return outdata

    except Exception as e:
        logging.exception(e)
        return data

 def gen_buttons(data):

     buttons = []

     for result in data:

         buttons.append([
             InlineKeyboardButton(result['name'], url=result['url'])
         ])

     return buttons
 def humanize_sec(sec:int):
     """Turn Seconds Into Days, Hours, Minutes"""

     days = int(sec/(60*60*24))
     daysec = days*60*60*24
     hrs:int = int((sec-daysec)/(60*60))
     hrsec = hrs*60*60
     mins = int((sec-daysec-hrsec)/60)

     return f"{days} Days {hrs} Hours {mins} Mins"

async def search_imdb(q:str, max:int=1):
    """Search Imdb For Results"""

    url = urllib3.util.parse_url(f"https://v2.sg.media-imdb.com/suggestion/titles/{q[0]}/{q}.json").url
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res = await resp.json()
                results = res.get('d', False)
                if results:
                    return results[0:max]
                else:
                    return False
    except Exception as e:
        logging.exception(e)
        return False

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

def is_available(x, default="Unknown"):
    """A Proffessional Function to return default if text attrib absent"""

    if x is None:
        return default
    return x.text

async def get_imdb_info(id, default='Unknown'):

    """A Function To Scrape The Imdb page of a Movie to get details"""

    if os.path.exists(f"/imdbinfo/{id}.json"):
        try:
            with open(f'/app/imdbinfo/{id}.json', 'r') as file:
                data = json.load(file)

            print(f"Using Cached Results For {id}")

            return data
        except Exception as e:
            logging.exception(e)

    rawtitle, title, rating, votes, director, writers, stars, genres, plot, runtime, release, language = (default,default,default,default,default,default,default,default,default,default,default,default)

    try:
        url = f"https://www.imdb.com/title/{id}/"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    page = await resp.text()
        except Exception as e:
            logging.exception(e)
            return False
        
        root: html.HtmlElement = html.fromstring(page).body
        main: html.HtmlElement = root.find("./div[2]/main/div/section[1]")
        
        try:
            head: html.HtmlElement = main.find("./section/div[3]/section/section")
            rawtitle = is_available(head.find("./div[1]/div[1]/h1"), default)
            title = f"<a href='{url}'>{rawtitle}</a>"
            rating = is_available(head.find("./div[1]/div[2]/div/div[@data-testid='hero-rating-bar__aggregate-rating']/a/div/div/div[2]/div[@data-testid='hero-rating-bar__aggregate-rating__score']/span[1]"), default)
            votes = is_available(head.find("./div[1]/div[2]/div/div[@data-testid='hero-rating-bar__aggregate-rating']/a/div/div/div[2]/div[3]"), default)
            
            people: html.HtmlElement = head.find("./div[3]/div[2]/div[1]/div[3]/ul")
            director = href_list_string(people.findall("./li[1]/div/ul/li"))
            writers = href_list_string(people.findall("./li[2]/div/ul/li"))
            stars = href_list_string(people.findall("./li[3]/div/ul/li"))
        except:
            pass

        try:
            base : html.HtmlElement = main.find("./div/section/div/div[1]")
            
            storyline:html.HtmlElement = base.find("./section[@cel_widget_id='StaticFeature_Storyline']/div[2]")
            genres = href_list_string(storyline.findall("./ul[2]/li[@data-testid='storyline-genres']/div/ul/li"))
            plot = is_available(storyline.find("./div[@data-testid='storyline-plot-summary']/div[1]/div"), default)
            
            details: html.HtmlElement = base.find("./section[@cel_widget_id='StaticFeature_Details']/div[2]/ul")
            release = href_list_string(details.findall("./li[@data-testid='title-details-releasedate']/div/ul/li"))
            language = href_list_string(details.findall("./li[@data-testid='title-details-languages']/div/ul/li"))
            runtime = base.find("./section[@cel_widget_id='StaticFeature_TechSpecs']/div[2]/ul/li[@data-testid='title-techspec_runtime']/div").text_content()
        except:
            pass
    except Exception as e:
        logging.exception(e)

    return dict(
        rawtitle=rawtitle,
        title=title,
        link=url,
        rating=rating,
        votes=votes,
        director=director,
        writers=writers,
        stars=stars,
        genres=genres,
        plot=plot,
        release=release,
        language=language,
        runtime=runtime,
        id=id
    )

async def write_imdb_results(id, data):
    """Function To Save Imdb Data Of A Movie To A Json File"""

    if not os.path.exists('/app/imdbinfo'):
        os.mkdir('/app/imdbinfo')
    if os.path.exists(f'/app/imdbinfo/{id}.json'):
        return True

    with open(f'/app/imdbinfo/{id}.json', 'w') as file:
        json.dump(data, file)

    return True