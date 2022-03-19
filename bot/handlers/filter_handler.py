
import asyncio
from threading import Thread

from pyrogram import Client, filters
from pyrogram.types import Message, InlineQuery

from bot.plugins.auto_filter import auto_filter
from bot.plugins.gfilter import global_filter
from bot.plugins.mfilter import mfilter
from bot.plugins.inline import inline_imdb

@Client.on_message(filters.text & filters.group & ~filters.edited, group=0)
def auto_filter_manager(bot:Client, update:Message):

    af = Thread(target=auto_filter, args=(bot, update))
    af.start()


@Client.on_message(filters.text & ~filters.channel & ~filters.edited, group=1)
def manual_filters_manager(bot:Client, update:Message):

    mf = Thread(target=mfilter, args=(bot, update))
    mf.start()

@Client.on_message(filters.text & ~filters.channel & ~filters.edited, group=5)
def global_filters_manager(bot:Client, update:Message):

    gf = Thread(target=global_filter, args=(bot, update))
    gf.start()

@Client.on_inline_query(group=0)
async def inline_search_handler(bot:Client, update:InlineQuery):

    await inline_imdb(bot, update)