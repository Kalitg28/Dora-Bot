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
async def sudo_handler(bot:Client, update:Message):

    cmd = update.command[0]

    if cmd=='broadcast':
        await broadcast_all(bot, update)
    elif cmd=='concast':
        await connected_cast(bot, update)
    elif cmd=='add':
        await connect(bot, update)
    elif cmd=='del':
        await disconnect(bot, update)
    elif cmd=='delall':
        await delall(bot, update)
    elif cmd=='cleardvd':
        await clearpredvd(bot, update)

@Client.on_message(filters.regex(r"^\/") & filters.private, group=3)
async def pvt_handler(bot:Client, update:Message):

    cmd = update.command[0]
    print(cmd)

    if cmd=='start':
        await start(bot, update)
    elif cmd=='json':
        await get_json(bot, update)
    elif cmd=='batch':
        await batch(bot, update)
    elif cmd=='map':
        await help(bot, update)
    elif cmd=='about':
        await about(bot, update)
    elif cmd=='connect':
        await settings.connect(bot, update)
    elif cmd=='disconnect':
        await settings.disconnect(bot, update)
 
@Client.on_message(filters.regex(r"^\/") & ~filters.channel, group=3)
async def public_handler(bot:Client, update:Message):

    cmd = update.command[0]

    if cmd=='start':
        await start(bot, update)
    elif cmd=='map':
        await help(bot, update)
    elif cmd=='filter':
        await mfilter.new_filter(bot, update)
    elif cmd=='stop':
        await mfilter.stop_filter(bot, update)
    elif cmd=='filters':
        await mfilter.n_filter(bot, update)
    elif cmd=='gfilters':
        await gfilter.all_gfilter(bot, update)
    elif cmd=='broadcast':
        await broadcast(bot, update),
    elif cmd=='knight':
        await settings.new_knight(bot, update)
    elif cmd=='deknight':
        await settings.del_knight(bot, update)
    elif cmd=='connect':
        await settings.connect(bot, update)
    elif cmd=='settings':
        await settings.settings(bot, update)
    elif cmd=='stopglobal':
        await gfilter.stopglobal(bot, update)
    elif cmd=='startglobal':
        await gfilter.startglobal(bot, update)
    elif cmd=='autofilter':
        await toggle_af(bot, update)
    elif cmd=='setspell':
        await setspell(bot, update)
    elif cmd=='delspell':
        await delspell(bot, update)
    elif cmd=='setcaption':
        await setcaption(bot, update)
    elif cmd=='delcaption':
        await delcaption(bot, update)