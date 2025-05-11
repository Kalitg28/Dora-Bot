#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @MrPurple902

import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import PeerIdInvalid, ChatAdminInviteRequired, ChatAdminRequired
from pyrogram.types.messages_and_media.message import Message

from bot.database import Database
from bot import Translation

from bot import VERIFY # pylint: disable=import-error

db = Database()


async def settings(bot, update: Message):
    
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    chat_type = update.chat.type
    global VERIFY

    if chat_type=="private" :

        chat_id = await db.get_conn(user_id)
        if not chat_id :

            await update.reply("<b>Please Connect To A Chat First Using The <code>/connect</code> Command To Use The Settings Panel From PM</b>", parse_mode="html")
            return

    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        admin_list.append(Translation.OWNER_ID)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)): # Checks if user is admin of the chat
        return
    
    bot_info = await bot.get_me()
    bot_first_name= bot_info.first_name
    settings = await db.find_chat(int(chat_id))
    try :
        chat_name = await bot.get_chat(int(chat_id))
        chat_name = chat_name.title
    except PeerIdInvalid:
        await update.reply_text("Looks Like I Couldnt Access This Chat Make Sure This Chat ID is valid And I am an admin There")
        return
    
    mp_count = settings["configs"]["max_pages"]
    mf_count = settings["configs"]["max_results"]
    mr_count = settings["configs"]["max_per_page"]
    accuracy_point = settings["configs"].get("accuracy", 0.70)
    caption = settings.get("caption", None)
    fsub = settings.get("fsub", None)
    spell = settings.get("noresult", None)
    auto_filter = settings.get('af', True)
    size_button = settings.get('size', False)
    g_filter = settings.get('global', True)
    fsub_msg = settings.get('fsub_msg', False)
    autodel = settings.get('autodel', False)
    
    text=f"<i><b>Configure Your <u><code>{chat_name}</code></u> Group's Auto Filter Settings...</b></i>\n"
    
    text+=f"\n<i>{chat_name}</i> Current Settings:\n"

    text+=f"\n- Auto Filter: {'Activated ✅' if auto_filter else 'Inactive ❌'}\n"

    text+=f"\n - Max Filter: <code>{mf_count}</code>\n"
    
    text+=f"\n - Max Pages: <code>{mp_count}</code>\n"
    
    text+=f"\n - Max Filter Per Page: <code>{mr_count}</code>\n"

    text+=f"\n - Accuracy Percentage: <code>{accuracy_point}</code>\n"

    if not fsub:
        text+=f"\n - Force Subscribe: Inactive ❌\n"
    else:
        text+=f"\n- Force Subscribe: {fsub['title']} ✅\n"

    text+=f"\n- Fsub Message : {'Custom ✅' if fsub_msg else 'Default'}\n"

    text+=f"\n- Custom Caption: {'Activated ✅' if caption else 'Inactive ❌'}\n"

    text+=f"\n- Spelling Check: {'Activated ✅' if spell else 'Inactive ❌'}\n"

    text+=f"\n- Size Button: {'Enabled ✅' if size_button else 'Disabled ❌'}\n"

    text+=f"\n- Auto Delete: {f'{autodel/60} mins' if autodel else 'Disabled ❌'}\n"
    
    text+="\nAdjust Above Value Using Buttons Below... "
    buttons=[
        [
            InlineKeyboardButton
                (
                    "📃 Filter Per Page📃 ", callback_data=f"mr_count({mr_count}|{chat_id})"
                ), 
    
            InlineKeyboardButton
                (
                    "📂 Max Pages 📂",       callback_data=f"mp_count({mp_count}|{chat_id})"
                )
        ]
    ]

    
    if spell:
        spell_button = InlineKeyboardButton('🖋️ Spell Check 🖋️', callback_data=f'spell(on|{chat_id})')
    else :
        spell_button = InlineKeyboardButton('🖋️ Spell Check 🖋️', callback_data=f'spell(off|{chat_id})')

    if caption:
        capt_button = InlineKeyboardButton('⛱ Caption ⛱', callback_data=f'capt(on|{chat_id})')
    else:
        capt_button = InlineKeyboardButton('⛱ Caption ⛱', callback_data=f'capt(off|{chat_id})')

    if auto_filter:
        af = InlineKeyboardButton('Auto Filter', callback_data=f'af(on|{chat_id})')
        
    else:
        af = InlineKeyboardButton('Auto Filter', callback_data=f'af(off|{chat_id})')

    if size_button:
        sb = InlineKeyboardButton('Size Button', callback_data=f'size(on|{chat_id})')
    else:
        sb = InlineKeyboardButton('Size Button', callback_data=f'size(off|{chat_id})')

    if g_filter:
        gf = InlineKeyboardButton('Global Filters', callback_data=f'global(on|{chat_id})')
        
    else:
        gf = InlineKeyboardButton('Global Filters', callback_data=f'global(off|{chat_id})')

    fmb = InlineKeyboardButton('Fsub Message', callback_data=f"fsub_msg({chat_id})")

    buttons.append([af, sb])    

    buttons.append([spell_button, capt_button])

    buttons.append([gf, fmb])

    if fsub:

        buttons.append(
            [
                InlineKeyboardButton
            (
                "🦾 Force Sub 🦾", callback_data=f'fsub(on|{chat_id})'
            ),
            InlineKeyboardButton
                (
                    "🔢 Total Results Count 🔢", callback_data=f"mf_count({mf_count}|{chat_id})"
                )
        
            ]
        )
    else :
        buttons.append(
            [
                InlineKeyboardButton
            (
                "🦾 Force Sub 🦾", callback_data=f'fsub(off|{chat_id})'
            ),
            InlineKeyboardButton
                (
                    "🔢 Total Results Count 🔢", callback_data=f"mf_count({mf_count}|{chat_id})"
                )
        
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton
                (
                    "🎯 Result's Accuracy 🎯", callback_data=f"accuracy({accuracy_point}|{chat_id})"
                ),
            InlineKeyboardButton
            (
                "AutoDelete", callback_data=f"autodel({chat_id})"
            )
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton
            (
                "Add Your Own Files", callback_data=f"gen_link({chat_id})"
            )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "✘ Close ✘", callback_data="close"
                )
        ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.reply_text( 
        text=text, 
        reply_markup=reply_markup, 
        parse_mode="html"
        )



async def connect(bot: Client, update: Message):

    text = update.text
    user_id = update.from_user.id
    chat_type = update.chat.type

    try :

        if chat_type in ('group','supergroup'):
            if update.from_user:
                member = await bot.get_chat_member(update.chat.id, update.from_user.id)
                if not member.status in ('creator','administrator'):
                    return
            buttons = [[InlineKeyboardButton("Connect To PM", url=f"http://t.me/Dora_MV_Bot?start=connect{update.chat.id}")]]
            await update.reply_text("Click On The Button Below To Connect To This Chat To Get PM Powers(Admins Only) :)", reply_markup=InlineKeyboardMarkup(buttons))
            return

        chat_id = text.replace("/connect", "").strip()
        chat_id = int(chat_id)

        try :

            link = await bot.export_chat_invite_link(chat_id=chat_id)
            grp = await bot.get_chat(chat_id)

            user = await bot.get_chat_member(chat_id,update.from_user.id)
            if not user.status in ("administrator","creator") :
                await update.reply("Nice Try You Non-Admin")
                return

        except PeerIdInvalid:

            await update.reply_text("This Doesnt Seem Like A Valid Chat ID \nMake Sure The ID is Correct if it is Make Sure I'm a member Of The Chat")
            return

        except ChatAdminInviteRequired:

            await update.reply_text("I Dont Have Enough Admin Permission Here Please Add Me To The Chat With Full Admin Permissions")
            return
        except ChatAdminRequired:
            
            await update.reply_text("Make Me An Admin In Your Group First")
            return
        
        except Exception as e :

            print(e)

        success = await db.conn_user(user_id, chat_id)

        if not success :

            await update.reply("Looks Like We Faced Some Problem Please Try Again Later")
        
        else :

            await update.reply(f"Woohoo... You're Now Successfully Connected To {grp.title} You Can Now Modify AutoFilter Settings And Edit Manual Filters From Here")

    except Exception as e :

        print(e)


async def disconnect(bot: Client, update: Message):

    user_id = update.from_user.id

    Result = await db.del_conn(user_id)
    
    if Result:

        await update.reply_text("Any Existing Connections Have Been Successfully Removed")

    else :

        await update.reply_text("Please Connect To A Chat First To Delete Connection")
        
async def new_knight(bot:Client, update:Message):

    if not update.from_user.id==Translation.OWNER_ID:
        return await update.reply_text('Nice Try Kid...')

    user = update.reply_to_message.from_user
    id = user.id

    success = await db.conn_user(id, 902)

    if not success:
        return await update.reply_text(f'Failed To Promote {user.mention} To A Knight :( ...')
    
    await update.reply_text(f'User {user.mention} Has Now Been Promoted To A Knight xD...')


async def del_knight(bot:Client, update:Message):
    if not update.from_user.id==Translation.OWNER_ID:
        return await update.reply_text('Nice Try Kid...')

    if update.reply_to_message:
        user = update.reply_to_message.from_user
        id = user.id
    else:
        id = int(update.text.split()[1])
        user = await bot.get_users(id)

    success = await db.del_conn(id)
    if success:
        await update.reply_text(f"Knight {user.mention} Was Demoted To A User :( ...")
    else:
        await update.reply_text(f"Demote Fialed...")
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F" 
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF" 
                               u"\U0001F1E0-\U0001F1FF" 
                               u"\U00002500-\U00002BEF" 
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"
                               u"\u3030"
    "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r' ', str(string))
