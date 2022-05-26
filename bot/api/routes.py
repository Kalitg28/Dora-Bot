# (c) @Jisin0

import logging
import re

from telegram import Bot, CallbackQuery, Message

from .clonecmd import botstats, broadcast, start, help, about 
from .multiselect import multiselect, cb_all, select, sensel
from .auto_filter import auto_filter
from .callback import cb_navg, cb_stats, edit

from .database import Database

from flask import request, Flask

app = Flask(__name__)
db = Database()

BOTS = {}

@app.route('/clones/<token>', methods=['POST'])
async def endpoint(token):
    """Function To Manage Incoming Requests"""

    data:dict = request.get_json(force=True)
    update = data

    global BOTS

    bot = BOTS.get(token, False)

    if not bot:
        bot = Bot(token)
        BOTS[token] = bot
        
    update["message"] = message = Message.de_json(update.get('message'), bot)
    update["callback_query"] = callback_query = CallbackQuery.de_json(update.get('callback_query'), bot)

    try:
        if message and message.text:
    
            text = message.text
            type = message.chat.type
    
            if type=='private':
                if text.startswith('/'):
                    command = text.split()[0][1:]
        
                    if command=='start':
                        await start(bot, message)
                        await db.add_user(bot.id, message.from_user.id)
                    elif command=='help':
                        await help(bot, message)
                    elif command=='about':
                        await about(bot, message)
                    elif command=='stats':
                        await botstats(bot, message)
                    elif command=='broadcast':
                        await broadcast(bot, message)
                    else:
                        pass
                else:
                    pass
                    
            elif type=='supergroup' or type=='group':
                await auto_filter(bot, message)
            else:
                pass

            return "Success", 200

        elif callback_query:

            querydata = callback_query.data

            if querydata.startswith('multi('):
                await multiselect(bot, callback_query)
            elif querydata.startswith('all('):
                await cb_all(bot, callback_query)
            elif querydata.startswith('sel('):
                await select(bot, callback_query)
            elif querydata.startswith('sensel('):
                await sensel(bot, callback_query)
            elif querydata.startswith('navigate('):
                await cb_navg(bot, callback_query)
            elif querydata.startswith('edit('):
                await edit(bot, callback_query)
            elif querydata=='stats':
                await cb_stats(bot, callback_query)

            return "Success", 200
        else:
            return "Not-Implemented", 200
    except Exception as e:
        logging.exception(e)
        return "Error", 200