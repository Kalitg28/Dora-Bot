from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto, InlineQueryResult
from bot.helpers import Helpers
import imdb
from imdb.Movie import Movie
from imdb.Person import Person
import random
from bot.translation import Translation


searcher = imdb.IMDb()

async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query

    results = await Helpers.all_imdb(text)

    if results:

        await update.answer(
            results=results,
            cache_time=0,
            switch_pm_text=f"Heres What I Found For {text}",
            switch_pm_parameter="",
            next_offset=""
        )
        
            
    else :

        await update.answer(results=[],
                        cache_time=0,
                        switch_pm_text=f'No Results Were Found For {text}',
                        switch_pm_parameter='')