# (c) @Jisin0

import re

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineQuery

from bot.plugins.callback import *
from bot.plugins.custom_cb import *
from bot.plugins.multiselect import *
from bot.plugins.inline import inline_imdb



@Client.on_inline_query(group=0)
async def inline_search_handler(bot:Client, update:InlineQuery):

    await inline_imdb(bot, update)

@Client.on_callback_query(group=0)
async def all_callbacks_manager(bot:Client, update:CallbackQuery):

    query = update.data

    if query.startswith('navigate('):
        await cb_navg(bot, update)
    elif query.startswith('multi('):
        await multiselect(bot, update)
    elif query.startswith('sel('):
        await select(bot, update)
    elif query.startswith('sensel('):
        await sensel(bot, update)
    elif query.startswith('all('):
        await cb_all(bot, update)
    elif query=='instruct':
        await callback_data(bot, update)
    elif query=='ignore':
        await ignore(bot, update)
    elif query.startswith('answer('):
        await answer_alert(bot, update)
    elif query.startswith('alert('):
        await alerter(bot, update)
    elif query.startswith('edit_t('):
        await edit_t(bot, update)
    elif query.startswith('edit_m('):
        await edit_m(bot, update)
    else:
        print(query)
        update.answer("Nee Etha Mwonusee...", show_alert=True)