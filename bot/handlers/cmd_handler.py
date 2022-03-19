import re

from pyrogram import Client, filters
from pyrogram.types import Message
from bot.plugins.batch import batch

from bot.plugins.broadcast import *
from bot.plugins.channel import connect, delall, disconnect
from bot.plugins.commands import *
from bot.plugins import mfilter, gfilter, settings
from bot.plugins.custom_cmd import delcaption, delspell, setcaption, setspell, toggle_af
from bot.translation import Translation

@Client.on_message(filters.regex(r"^\/") & filters.chat(Translation.OWNER_ID), group=4)
def sudo_handler(bot:Client, update:Message):

    cmd = update.text.split(None, 1)[0][1:]

    if cmd=='broadcast':
        broadcast_all(bot, update)
    elif cmd=='concast':
        connected_cast(bot, update)
    elif cmd=='add':
        connect(bot, update)
    elif cmd=='del':
        disconnect(bot, update)
    elif cmd=='delall':
        delall(bot, update)
    elif cmd=='cleardvd':
        clearpredvd(bot, update)

@Client.on_message(filters.regex(r"^\/") & ~filters.channel, group=3)
def pvt_handler(bot:Client, update:Message):

    cmd = update.text.split(None, 1)[0][1:]
    #type = update.chat.type
    
    if cmd=='start':
        start(bot, update)
    elif cmd=='json':
        get_json(bot, update)
    elif cmd=='batch':
        batch(bot, update)
    elif cmd=='map':
        help(bot, update)
    elif cmd=='about':
        about(bot, update)
    elif cmd=='connect':
        settings.connect(bot, update)
    elif cmd=='disconnect':
        settings.disconnect(bot, update)
    elif cmd=='filter':
        mfilter.new_filter(bot, update)
    elif cmd=='stop':
        mfilter.stop_filter(bot, update)
    elif cmd=='filters':
        mfilter.n_filter(bot, update)
    elif cmd=='gfilters':
        gfilter.all_gfilter(bot, update)
    elif cmd=='broadcast':
        broadcast(bot, update),
    elif cmd=='knight':
        settings.new_knight(bot, update)
    elif cmd=='deknight':
        settings.del_knight(bot, update)
    elif cmd=='connect':
        settings.connect(bot, update)
    elif cmd=='settings':
        settings.settings(bot, update)
    elif cmd=='stopglobal':
        gfilter.stopglobal(bot, update)
    elif cmd=='startglobal':
        gfilter.startglobal(bot, update)
    elif cmd=='autofilter':
        toggle_af(bot, update)
    elif cmd=='setspell':
        setspell(bot, update)
    elif cmd=='delspell':
        delspell(bot, update)
    elif cmd=='setcaption':
        setcaption(bot, update)
    elif cmd=='delcaption':
        delcaption(bot, update)
 
@Client.on_message(filters.regex(r"^\/") & ~filters.channel, group=3)
def public_handler(bot:Client, update:Message):

    cmd = update.text.split(None, 1)[0][1:]

    if cmd=='start':
        start(bot, update)
    elif cmd=='map':
        help(bot, update)
    