import re

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

from bot.plugins.callback import *
from bot.plugins.custom_cb import *
from bot.plugins.multiselect import *

@Client.on_callback_query(group=0)
def all_callbacks_manager(bot:Client, update:CallbackQuery):

    query = update.data

    if query.startswith('navigate('):
        cb_navg(bot, update)
    elif query.startswith('multi('):
        multiselect(bot, update)
    elif query.startswith('sel('):
        select(bot, update)
    elif query.startswith('sensel('):
        sensel(bot, update)
    elif query.startswith('all('):
        cb_all(bot, update)
    elif query.startswith('settings('):
        cb_settings(bot, update)
    elif query=='close':
        callback_data(bot, update)
    elif query=='instruct':
        callback_data(bot, update)
    elif query=='ignore':
        ignore(bot, update)
    elif query.startswith('answer('):
        answer_alert(bot, update)
    elif query=='stats':
        cb_stats(bot, update)
    elif query.startswith('edit_c('):
        edit_caption(bot, update)
    elif query.startswith('fix('):
        fix_value(bot, update)
    elif query.startswith('fsub_msg('):
        toggle_fsubmsg(bot, update)
    elif query.startswith('af('):
        toggle_af(bot, update)
    elif query.startswith('size('):
        size_button(bot, update)
    elif query.startswith('capt('):
        custom_cap(bot, update)
    elif query.startswith('fsub('):
        fsub(bot, update)
    elif query.startswith('global('):
        global_filters(bot, update)
    elif query.startswith('spell('):
        spell_check(bot, update)
    elif query.startswith('gen_link('):
        private_link_gen(bot, update)
    elif query.startswith('autodel('):
        autodel(bot, update)
    elif query.startswith('mr_count('):
        cb_max_buttons(bot, update)
    elif query.startswith('mf_count('):
        cb_max_results(bot, update)
    elif query.startswith('mp_count('):
        cb_max_page(bot, update)
    elif query.startswith('accuracy('):
        cb_accuracy(bot, update)
    elif query.startswith('set('):
        cb_set(bot, update)
    elif query.startswith('alert('):
        alerter(bot, update)
    elif query.startswith('edit_t('):
        edit_t(bot, update)
    elif query.startswith('edit_m('):
        edit_m(bot, update)
    else:
        print(query)
        update.answer("Nee Etha Mwonusee...", show_alert=True)