from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, Message, Photo, InlineQueryResultPhoto
from bot.helpers import Helpers

@Client.on_inline_query()
async def inline_imdb(bot:Client, update:InlineQuery):

    text = update.query

    results = await Helpers.all_imdb(text)
    if not results :
        await update.answer(results=[],
                        cache_time=0,
                        switch_pm_text='No Results Were Found')
        return

    elif len(results)<1:
        await update.answer(results=[],
                        cache_time=0,
                        switch_pm_text=f'No Results Were Found For {text}')
            
    else :

        await update.answer(
            results=results,
            cache_time=0
        )