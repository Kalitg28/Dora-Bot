
import asyncio
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import Message, InlineQuery

from bot.plugins.auto_filter import auto_filter
from bot.plugins.gfilter import global_filter
from bot.plugins.mfilter import mfilter
from bot.plugins.inline import inline_imdb

@Client.on_message(filters.text & filters.group & ~filters.edited, group=0)
async def auto_filter_manager(bot:Client, update:Message):

    af = Thread(target=asyncio.run, args=(auto_filter(bot, update),))
    af.start()

@Client.on_message(filters.text & ~filters.channel & ~filters.edited, group=1)
async def manual_filters_manager(bot:Client, update:Message):

    mf = Thread(target=asyncio.run, args=(mfilter(bot, update),))
    gf = Thread(target=asyncio.run, args=(global_filter(bot, update),))

    mf.start()
    gf.start()

@Client.on_inline_query(group=0)
async def inline_search_handler(bot:Client, update:InlineQuery):

    await inline_imdb(bot, update)