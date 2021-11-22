# (c) @MrPurple902

import re 
import imdb
from imdb import Movie


searcher = imdb.IMDb()
IMDB = {}

class Helpers() :

 
 async def get_movie(my_movie):

    info = ["localized title", "rating", "votes", "genres", "runtimes", "original air date", "full-size cover url", "kind"]

    movies = searcher.search_movie(my_movie)
    movie_id = movies[0].movieID
    movie = searcher.get_movie(movie_id, info=Movie.Movie.default_info)

    global IMDB

    movie_info = {}

    for key in info :

        try :

            movie_info[key] = movie.get(key)
            if not movie_info[key]:
                movie_info[key] = "Unknown"

        except Exception as e :

            print(e)

    if movie_info["kind"]!="movie":

        movie_info.pop("original air date")
        movie_info["originl air date"] = movie.get("year")

    try :

        runtime = int(movie_info["runtimes"])

        if runtime<=60:
            movie_info.pop("runtimes")
            movie_info["runtimes"] = f"{int(runtime/60)}hr {runtime%60}mins"

        else :

            movie_info.pop("runtimes")
            movie_info["runtimes"] = f"{runtime} mins"

    except:

        pass

    IMDB[my_movie] = movie_info

 async def cleanse(query:str):

    keywords = ["movie", "malayalam", "tamil", "kannada", "hd", "subtitle", "subtitles"]
    query = query.lower()
    for key in keywords:

        if key in query.split():

            query = query.replace(key, '')

    return query