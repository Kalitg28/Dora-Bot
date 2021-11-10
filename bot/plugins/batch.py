# (c) @MrPurple902

import re

from pyromod import listen
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, MessageIdInvalid

@Client.on_message(filters.command("batch") & filters.private & ~filters.bot, group=1)
async def batch(bot:Client, update:Message):

    user_id = update.from_user.id

    post1:Message = await bot.ask(chat_id=update.chat.id, text="Please Forward The First Post From The Channel (Where I Am an admin)", timeout=360)
    if not post1: return

    if not post1.forward_from_chat:

        await update.reply_text("Please Forward The Message With Quotes (ie : Forwarded From ...)")
        return

    chat_id1 = post1.forward_from_chat.id
    try :

        msg_id1 = post1.forward_from_message_id
        await bot.get_messages(
            chat_id=chat_id1,
            message_ids=msg_id1
        )
    except PeerIdInvalid:
        return await update.reply_text("Looks like Im Not A Member Of The Chat Where This Message Is Posted")
    except MessageIdInvalid:
        return await update.reply_text("Looks Like The Message You Forwarded No Longer Exists")
    except Exception as e:
        print(e)
        return await update.reply_text("Something Went Wrong Please Try Again Later")

    post2 = await bot.ask(chat_id=update.chat.id, text="Now Forward The Last Message From The Same Channel", timeout=360)
    if not post2 : return

    chat_id2 = post2.forward_from_chat.id
    if not chat_id1==chat_id2 :
        return await update.reply_text("These Two Messages Arent From The Same Chat")

    try :

        msg_id2 = post2.forward_from_message_id
        await bot.get_messages(
            chat_id=chat_id2,
            message_ids=msg_id2
        )
    except PeerIdInvalid:
        return await update.reply_text("Looks like Im Not A Member Of The Chat Where This Message Is Posted")
    except MessageIdInvalid:
        return await update.reply_text("Looks Like The Message You Forwarded No Longer Exists")
    except Exception as e:
        print(e)
        return await update.reply_text("Something Went Wrong Please Try Again Later")

    if not msg_id1<=msg_id2:
        return await update.reply_text("The First Message Has To Be Posted Above The Second In The Channel To Generate A Batch")

    encoded = await encode(f"{str(chat_id1).replace('-100','')} {msg_id1} {msg_id2}")
    url = f"https://t.me/DoraFilterBot?start=a{encoded}"

    await update.reply_text(f"Woohoo... I've Successfully Generated A Link For Your Batch\n{url}\nPS:This Link Will Only Work As Long As I AM An Admin In The From Channel")

async def encode(text:str):
    string = text
    encoder = {'1': 'B', '2':'Y', '3':'i', '4':'P', '5':'q', '6':'k', '7':'r', '8':'R', '9':'J', '0':'h', ' ':'a'}

    for key in encoder.keys():
        string = string.replace(key, encoder[key])

    return string.strip()

class Batch():

    def decode(text:str):

        string = text
        decoder = {'B':'1', 'Y':'2',  'i':'3', 'P':'4', 'q':'5', 'k':'6', 'r':'7', 'R':'8', 'J':'9', 'h':'0', 'a':' '}

        for key in decoder.keys():
            string = string.replace(key, decoder[key])
    
        return string.strip()

    async def get_batch(batch:str, bot:Client, update:Message):

        user_id = update.chat.id

        try :

            channel_id, msg1, msg2 = re.findall(r"^a(.+)a(.+)a(.+)", batch)[0]
            channel_id, msg1, msg2 = (Batch.decode(channel_id), Batch.decode(msg1), Batch.decode(msg2))
            for id in range(int(msg1), int(msg2)):
                try :
                    message = await bot.get_messages(chat_id=int(channel_id), message_ids=id)
                    file = message.document or\
                  message.video or\
                  message.photo or\
                  message.audio or\
                  message.animation or\
                  message.sticker
                    if message.reply_markup.inline_keyboard:
                        btn = message.reply_markup.inline_keyboard
                        if file:
                            caption = "" if not message.caption.html else message.caption.html
                            await bot.copy_message(
                                chat_id=user_id,
                                from_chat_id=int(channel_id),
                                message_id=id,
                                parse_mode="html",
                                reply_markup=InlineKeyboardMarkup(btn),
                                caption=caption
                            )
                        else:
                            await bot.copy_message(
                                chat_id=user_id,
                                from_chat_id=int(channel_id),
                                message_id=id,
                                parse_mode="html",
                                reply_markup=InlineKeyboardMarkup(btn)
                            )
                    else:
                        if file:
                            caption = "" if not message.caption.html else message.caption.html
                            await bot.copy_message(
                                chat_id=user_id,
                                from_chat_id=int(channel_id),
                                message_id=id,
                                parse_mode="html",
                                caption=caption
                            )
                        else:
                            await bot.copy_message(
                                chat_id=user_id,
                                from_chat_id=int(channel_id),
                                message_id=id,
                                parse_mode="html",
                            )
                except MessageIdInvalid:
                    pass
                except PeerIdInvalid:
                    await update.reply_text("Failed To Get Messages\nReason : Im not A Member of The Original Channel")
                except Exception as e:
                    print(e)
        except Exception as e : print(e)
