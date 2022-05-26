# (c) @Jisin0
import logging
from time import time
import re
import os

from telegram import Bot, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import constants
from telegram.error import Unauthorized
from .database import Database
from .helpers import Helpers
from .configs import BUTTONS, DICTIONARY

db = Database()

DORA = Bot(os.environ['BOT_TOKEN'])
FILES_CHANNEL = int(os.environ["CLONE_FILES"])

BCAST = {}

async def start(bot:Bot, update:Message):
    """Manage The Clone's Start Command"""

    args = update.text.split(None, 1)
    if len(args)>1:
        file_uid = args[1]

        if file_uid.startswith('retry'):
            from_chat, message_id = re.findall(r'retryz(.+)z', file_uid)[0].split('a', 1)
            return update.reply_text("Now Please Return And Try Again :)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", url=f"https://t.me/c/{from_chat}/{message_id}")]]), quote=True)

        results = re.findall(r"^z(.+)z(.+)z$", file_uid)[0]
        if len(results)<2: 
            return update.reply_text("Thats Not A Valid Url :(", quote=True)
        new_uid = results[0]
        group_id = Helpers.decode(results[1])

        file_id, file_name, file_caption, file_type, copy_message_id = await db.get_file(new_uid)
        
        if (file_id or file_type) == None:
            return
        
        file_caption = "<b>" + file_name + "</b>\n\n"
        try:
            if copy_message_id:
                bot.copy_message(
                    chat_id=update.chat_id,
                    from_chat_id=FILES_CHANNEL,
                    message_id=copy_message_id,
                    caption=file_caption,
                    parse_mode='HTML'
                )
            else:
                msg = DORA.send_document(
                chat_id=FILES_CHANNEL,
                document=file_id,
                caption=file_caption,
                parse_mode='HTML'
                )

                await db.update_copy_id(new_uid, FILES_CHANNEL, msg.message_id)

                bot.copy_message(
                    chat_id=update.chat_id,
                    from_chat_id=FILES_CHANNEL,
                    message_id=msg.message_id,
                    caption=file_caption,
                    parse_mode='HTML'
                )
        except Exception as f:

            logging.exception(f)

            try:
                msg = DORA.send_document(
                    chat_id=update.chat.id,
                    document=file_id,
                    caption=file_caption,
                    parse_mode='HTML'
                )
    
                update.reply_text(
                    f"<i><b>Successfully Uploaded Your Requested File </b></i>: \n<code>{file_name}</code>\n\nClick The Button Below To Reach Your File 👇",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Click Here", url=f"t.me/DoraFilterBot/{msg.message_id}")]]),
                    parse_mode='HTML'
                )
            except Unauthorized:
                buttonurl=f't.me/DoraFilterBot?start=retryz{bot.id}a{update.message_id+1}z'
                markup = [
                    [
                        InlineKeyboardButton("Retry", url=f't.me/{bot.username}?start={args}'),
                        InlineKeyboardButton("C L I C K  H E R E", url=buttonurl)
                    ]
                ]
    
                await update.reply_text(f"You Havent Started My Master Bot :(\nCick on The Link Below And Return Here \n\n<a href='{buttonurl}'> C L I C K  H E R E </a>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(markup))
            except Exception as e:
                logging.exception(e)
    
                await update.reply_text(f"Looks Like I Ran Into A Problem Please Contact My Support Team :(\n\n<code>{e}</code>", parse_mode='HTML')
        return



    pic = await db.get_bot_setting(bot.id, 'start_photo')
    if not pic:
        pic = "https://static.turbosquid.com/Preview/2020/08/18__04_34_57/Still_1.jpgC9E5FEBE-F1D6-43A0-AAAF-75B860A036D3Large.jpg"
    text:str = await db.get_bot_setting(bot.id, 'start_text')
    if not text:
        text = DICTIONARY.EN["START"]

    text = text.format(mention=update.from_user.mention_html(),
    first_name=update.from_user.first_name,
    last_name=update.from_user.last_name,
    full_name=update.from_user.last_name,
    id=update.from_user.id,
    username=update.from_user.name)

    markup = InlineKeyboardMarkup(BUTTONS.EN["START"])

    if pic:
        try:
            update.reply_photo(pic, text, parse_mode=constants.PARSEMODE_HTML, reply_markup=markup)
        except Exception as e:
            update.reply_text(text, parse_mode=constants.PARSEMODE_HTML, reply_markup=markup)
            logging.exception(e)
    else:
        update.reply_text(text, parse_mode=constants.PARSEMODE_HTML, reply_markup=markup)

async def help(bot:Bot, update:Message):

    update.reply_text(
        text=DICTIONARY.EN['HELP'],
        reply_markup=InlineKeyboardMarkup(BUTTONS.EN.get('HELP', BUTTONS.EN['DEFAULT'])),
        parse_mode='HTML'
    )

async def about(bot:Bot, update:Message):

    update.reply_text(
        text=DICTIONARY.EN['ABOUT'],
        reply_markup=InlineKeyboardMarkup(BUTTONS.EN.get('ABOUT', BUTTONS.EN['DEFAULT'])),
        parse_mode='HTML'
    )

async def botstats(bot:Bot, update:Message):

    stat = await db.get_bot_stats(bot.id)

    text = f"""
U S E R S : {stat['usercount']}
R E Q U E S T S : {stat['requests']}
U P T I M E : {Helpers.humanize_sec(time()-stat['created'])}
A C T I V E : {stat['active']}
"""
    update.reply_text(text, reply_markup=InlineKeyboardMarkup(BUTTONS.EN['STATS']), quote=True)

async def broadcast(bot:Bot, update:Message):

    admins = await db.get_admins(bot.id)

    if not update.from_user.id in admins:

        update.reply_text("You Are Unauthorized To Do That It Is An Admin Only Command :(", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Make Your Own Bot ?", url='t.me/DoraFilterBot?start=clonetutorial')]]), quote=True)
        return
    
    stat = update.reply_text("<code>Verifying And Gathering Resources ...</code>", parse_mode='HTML', quote=True)

    if not update.reply_to_message:
        stat.edit_text("Please Reply This Command To The Message You Would Like To Broadcast :(", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Watch A Tutorial", url='t.me/DoraFilterBot?start=clonetutorial_broadcast')]]), quote=True)
        return

    users = await db.get_all_users(bot.id)

    msg = update.reply_to_message

    if msg.text:
        caption = None
    else:
        caption = msg.caption_html

    markup = msg.reply_markup

    success = 0
    blocked = 0
    failed = 0

    for user in users:

        try:
            update.reply_to_message.copy(
                chat_id=user,
                caption=caption,
                parse_mode='HTML',
                reply_markup=markup
            )
            success+=1
        except Unauthorized:
            blocked+=1
        except Exception as e:
            print(e)
            failed+=1

        stat.edit_text(
            text=f"Current Broadcast Stats :\n\nSuccess : {success}\nBlocked : {blocked}\nFailed : {failed}"
        )

    stat.edit_text(
        f"Broadcast Completed !! :\n\nSuccess : {success}\nBlocked : {blocked}\nFailed : {failed}"
    )