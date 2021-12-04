from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto
from bot.helpers import Helpers

@Client.on_inline_query()
async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query

    results = await Helpers.all_imdb(text)

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