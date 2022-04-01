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

    if query.startswith('settings('):
        await cb_settings(bot, update)
    elif query=='close':
        await callback_data(bot, update)
    elif query=='stats':
        await cb_stats(bot, update)
    elif query.startswith('edit_c('):
        await edit_caption(bot, update)
    elif query.startswith('fix('):
        await fix_value(bot, update)
    elif query.startswith('fsub_msg('):
        await toggle_fsubmsg(bot, update)
    elif query.startswith('af('):
        await toggle_af(bot, update)
    elif query.startswith('size('):
        await size_button(bot, update)
    elif query.startswith('capt('):
        await custom_cap(bot, update)
    elif query.startswith('fsub('):
        await fsub(bot, update)
    elif query.startswith('global('):
        await global_filters(bot, update)
    elif query.startswith('spell('):
        await spell_check(bot, update)
    elif query.startswith('gen_link('):
        await privat_link_gen(bot, update)
    elif query.startswith('autodel('):
        await autodel(bot, update)
    elif query.startswith('mr_count('):
        await cb_max_buttons(bot, update)
    elif query.startswith('mf_count('):
        await cb_max_results(bot, update)
    elif query.startswith('mp_count('):
        await cb_max_page(bot, update)
    elif query.startswith('accuracy('):
        await cb_accuracy(bot, update)
    elif query.startswith('set('):
        await cb_set(bot, update)