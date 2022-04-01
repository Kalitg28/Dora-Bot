import re
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot import start_uptime, Translation, Buttons, VERIFY # pylint: disable=import-error
from bot.handlers.auto_filter import ( # pylint: disable=import-error
    INVITE_LINK, 
    ACTIVE_CHATS
    )

from bot.database import Database
from bot.helpers import read_results_from_file # pylint: disable=import-error

db = Database()


async def cb_navg(bot, update: CallbackQuery):
    """
    A Callback Funtion For The Next Button Appearing In Results
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    index_val, btn, query = re.findall(r"navigate\((.+)\)", query_data)[0].split("|", 2)
    try:
        ruser_id = update.message.reply_to_message.from_user.id
    except Exception as e:
        print(e)
        ruser_id = None
    
    admin_list = VERIFY.get(str(chat_id))
    if admin_list == None: # Make Admin's ID List
        
        admin_list = []
        
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
            
        admin_list.append(None) # Just For Anonymous Admin....
        VERIFY[str(chat_id)] = admin_list
    
    if not ((user_id == ruser_id) or (user_id in admin_list)): # Checks if user is same as requested user or is admin
        await update.answer("Nice Try ;)",show_alert=True)
        return


    if btn == "next":
        index_val = int(index_val) + 1
    elif btn == "back":
        index_val = int(index_val) - 1
    
    achats = ACTIVE_CHATS[str(chat_id)]
    configs = await db.find_chat(chat_id)
    pm_file_chat = configs["configs"]["pm_fchat"]
    show_invite = configs["configs"]["show_invite_link"]
    show_invite = (False if pm_file_chat == True else show_invite)

    FIND = await read_results_from_file(chat_id, query)
    if not FIND:
        return await update.answer("Looks Like This Request No LOnger Exists :(")
    results = FIND.get(query).get("results")
    max_pages = FIND.get(query).get("max_pages")
    FIND = {}
    
    try:
        temp_results = results[index_val].copy()
    except IndexError:
        return # Quick Fix🏃🏃
    except Exception as e:
        print(e)
        return

    if ((index_val + 1 )== max_pages) or ((index_val + 1) == len(results)): # Max Pages

        if not index_val <= 0:
            
            temp_results.append([
            InlineKeyboardButton("⇚ ʙᴀᴄᴋ", callback_data=f"navigate({index_val}|back|{query})")
        ])

    elif int(index_val) <= 0:
        temp_results.append(
                [
                    InlineKeyboardButton(f"📃 ᴘᴀɢᴇ 1/{len(results) if len(results) < max_pages else max_pages} 📃", callback_data="ignore"),
                    InlineKeyboardButton("ɴᴇxᴛ ⇛", callback_data=f"navigate(0|next|{query})")
                ]
            )

    else:
        temp_results.append([
            InlineKeyboardButton("⇚ ʙᴀᴄᴋ", callback_data=f"navigate({index_val}|back|{query})"),
            InlineKeyboardButton("ɴᴇxᴛ ⇛", callback_data=f"navigate({index_val}|next|{query})")
        ])

    if not int(index_val) == 0:    
        temp_results.append([
            InlineKeyboardButton(f"📃 ᴘᴀɢᴇ {index_val + 1}/{len(results) if len(results) < max_pages else max_pages} 📃", callback_data="ignore")
        ])

    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ɪɴғᴏ", callback_data="answer(INFO)"), InlineKeyboardButton(f"ᴀʟʟ", callback_data=f"all({query})"), InlineKeyboardButton("sᴇʟᴇᴄᴛ", callback_data=f"multi({index_val}|{query})")]]+temp_results)
    
    try:
        await update.message.edit_reply_markup(
                reply_markup=reply_markup
        )
        
    except FloodWait as f: # Flood Wait Caused By Spamming Next/Back Buttons
        await asyncio.sleep(f.x)
        await update.message.edit_reply_markup(
                reply_markup=reply_markup
        )



async def cb_settings(bot, update: CallbackQuery):
    """
    A Callback Funtion For Back Button in /settings Command
    """
    chat_id = update.message.chat.id
    user_id = update.from_user.id if update.from_user else None
    chat_type = update.message.chat.type
    global VERIFY

    if chat_type=="private" :

        chat_id = await db.get_conn(user_id)
        if not chat_id :

            await update.message.reply("<b>Please Connect To A Chat First Using The <code>/connect</code> Command To Use The Settings Panel From PM</b>", parse_mode="html")
            return


    if not user_id in VERIFY.get(str(chat_id)): # Checks if user is admin of the chat
        return
    
    bot_info = await bot.get_me()
    bot_first_name= bot_info.first_name
    settings = await db.find_chat(int(chat_id))
    try :
        chat_name = await bot.get_chat(int(chat_id))
        chat_name = chat_name.title
    except PeerIdInvalid:
        await update.message.reply_text("Looks Like I Couldnt Access This Chat Make Sure This Chat ID is valid And I am an admin There")
    
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
        text+=f"\n - Force Subscribe: {fsub['title']} ✅\n"

    text+=f"\n- Fsub Message : {'Custom ✅' if fsub_msg else 'Default'}\n"

    text+=f"\n- Custom Caption: {'Activated ✅' if caption else 'Inactive ❌'}\n"

    text+=f"\n- Custom Caption: {'Activated ✅' if caption else 'Inactive ❌'}\n"

    text+=f"\n- Spelling Check: {'Activated ✅' if spell else 'Inactive ❌'}\n"

    text+=f"\n- Size Button: {'Enabled ✅' if size_button else 'Disabled ❌'}\n"

    text+=f"\n- Auto Delete: {f'{autodel/60} mins' if autodel else 'Disabled ❌'}\n"
    
    text+="\nAdjust Above Value Using Buttons Below... "
    buttons=[
        [
            InlineKeyboardButton
                (
                    "📃 Filter Per Page 📃 ", callback_data=f"mr_count({mr_count}|{chat_id})"
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
    
    await update.message.edit_text (
        text=text, 
        reply_markup=reply_markup, 
        parse_mode="html",
        )


async def cb_max_buttons(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Result To Be Shown Per Page
    """
    global VERIFY
    query_data = update.data
    chat_type = update.message.chat.type

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        chat_name = "Your Group"
        if not chat_id:
            return
    else :
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mr_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>Choose Your Desired 'Max Filter Count Per Page' For Every Filter Results Shown In</i> <code>{chat_name}</code>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "5 Filters", callback_data=f"set(per_page|5|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "7 Filters", callback_data=f"set(per_page|7|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 Filters", callback_data=f"set(per_page|10|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "12 Filters", callback_data=f"set(per_page|12|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "15 Filters", callback_data=f"set(per_page|15|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "17 Filters", callback_data=f"set(per_page|17|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "20 Filters", callback_data=f"set(per_page|20|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "22 Filters", callback_data=f"set(per_page|22|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "25 Filters", callback_data=f"set(per_page|25|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "27 Filters", callback_data=f"set(per_page|27|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "30 Filters", callback_data=f"set(per_page|30|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "32 Filters", callback_data=f"set(per_page|32|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "40 Filters", callback_data=f"set(per_page|40|{chat_id}|{count})"
                ),
            InlineKeyboardButton
                (
                    "45 Filters", callback_data=f"set(per_page|45|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



async def cb_max_page(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Result Pages To Be Shown
    """
    global VERIFY
    query_data = update.data
    chat_type = update.message.chat.type

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        chat_name = "Your Group"
        if not chat_id:
            return
    else :
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mp_count\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i>Choose Your Desired 'Max Filter Page Count' For Every Filter Results Shown In</i> <code>{chat_name}</code>"
    
    buttons = [

        [
            InlineKeyboardButton
                (
                    "2 Pages", callback_data=f"set(pages|2|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "4 Pages", callback_data=f"set(pages|4|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "6 Pages", callback_data=f"set(pages|6|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "8 Pages", callback_data=f"set(pages|8|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "10 Pages", callback_data=f"set(pages|10|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]

    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



async def cb_max_results(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Count Of Maximum Files TO Be Fetched From Database
    """
    global VERIFY
    query_data = update.data
    chat_type = update.message.chat.type

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        chat_name = "Your Group"
        if not chat_id:
            return
    else :
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    count, chat_id = re.findall(r"mf_count\((.+)\)", query_data)[0].split("|", 1)

    text = f"<i>Choose Your Desired 'Max Filter' To Be Fetched From DB For Every Filter Results Shown In</i> <code>{chat_name}</code>"

    buttons = [

        [
            InlineKeyboardButton
                (
                    "50 Results", callback_data=f"set(results|50|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "100 Results", callback_data=f"set(results|100|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "150 Results", callback_data=f"set(results|150|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "200 Results", callback_data=f"set(results|200|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "250 Results", callback_data=f"set(results|250|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "300 Results", callback_data=f"set(results|300|{chat_id}|{count})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )

async def cb_accuracy(bot, update: CallbackQuery):
    """
    A Callaback Funtion to control the accuracy of matching results
    that the bot should return for a query....
    """
    global VERIFY
    chat_type = update.message.chat.type

    if chat_type=="private":
        chat_id = await db.get_conn(update.from_user.id)
        chat_name = "Your Group"
        if not chat_id:
            return
    else :
        chat_id = update.message.chat.id
        chat_name = update.message.chat.title
    user_id = update.from_user.id
    query_data = update.data
    
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    val, chat_id = re.findall(r"accuracy\((.+)\)", query_data)[0].split("|", 1)
    
    text = f"<i>Choose Your Desired 'Accuracy Perceentage' For Every Filter Results Shown In</i> <code>{chat_name}</code>\n\n"
    text+= f"<i>NB: Higher The Value Better Matching Results Will Be Provided... And If Value Is Lower It Will Show More Results \
        Which Is Fimilary To Query Search (Wont Be Accurate)....</i>"

    buttons = [
        [
            InlineKeyboardButton
                (
                    "100 %", callback_data=f"set(accuracy|1.00|{chat_id}|{val})"
                ),
            InlineKeyboardButton
                (
                    "90 %", callback_data=f"set(accuracy|0.90|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "80 %", callback_data=f"set(accuracy|0.80|{chat_id}|{val})"
                ),
            InlineKeyboardButton
                (
                    "70 %", callback_data=f"set(accuracy|0.70|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "65 %", callback_data=f"set(accuracy|0.65|{chat_id}|{val})"
                ),
            InlineKeyboardButton
                (
                    "60 %", callback_data=f"set(accuracy|0.60|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "55 %", callback_data=f"set(accuracy|0.55|{chat_id}|{val})"
                ),
            InlineKeyboardButton
                (
                    "50 %", callback_data=f"set(accuracy|0.50|{chat_id}|{val})"
                )
        ],
        [
            InlineKeyboardButton
            (
                "45 %", callback_data=f"set(accuracy|0.45|{chat_id}|{val})"
            ),
            InlineKeyboardButton
            (
                "40 %", callback_data=f"set(accuracy|0.40|{chat_id}|{val})"
            )
        ],
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



async def cb_set(bot, update: CallbackQuery):
    """
    A Callback Funtion Support For config()
    """
    global VERIFY
    query_data = update.data
    user_id = update.from_user.id

    action, val, chat_id, curr_val = re.findall(r"set\((.+)\)", query_data)[0].split("|", 3)
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    try:
        val, chat_id, curr_val = float(val), int(chat_id), float(curr_val)
    except:
        chat_id = int(chat_id)
    
    if val == curr_val:
        await update.answer("New Value Cannot Be Old Value...Please Choose Different Value...!!!", show_alert=True)
        return
    
    prev = await db.find_chat(chat_id)

    accuracy = float(prev["configs"].get("accuracy", 0.70))
    max_pages = int(prev["configs"].get("max_pages"))
    max_results = int(prev["configs"].get("max_results"))
    max_per_page = int(prev["configs"].get("max_per_page"))
    pm_file_chat = True if prev["configs"].get("pm_fchat") == (True or "True") else False
    show_invite_link = True if prev["configs"].get("show_invite_link") == (True or "True") else False
    
    if action == "accuracy": # Scophisticated way 😂🤣
        accuracy = val
    
    elif action == "pages":
        max_pages = int(val)
        
    elif action == "results":
        max_results = int(val)
        
    elif action == "per_page":
        max_per_page = int(val)

    elif action =="showInv":
        show_invite_link = True if val=="True" else False

    elif action == "inPM":
        pm_file_chat = True if val=="True" else False
        

    new = dict(
        accuracy=accuracy,
        max_pages=max_pages,
        max_results=max_results,
        max_per_page=max_per_page,
        pm_fchat=pm_file_chat,
        show_invite_link=show_invite_link
    )
    
    append_db = await db.update_configs(chat_id, new)
    
    if not append_db:
        text="Something Wrong Please Check Bot Log For More Information...."
        await update.answer(text=text, show_alert=True)
        return
    
    text=f"Your Request Was Updated Sucessfully....\nNow All Upcoming Results Will Show According To This Settings..."
        
    buttons = [
        [
            InlineKeyboardButton
                (
                    "Back ⇚", callback_data=f"settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close ✘", callback_data="close"
                )
        ]
    ]
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )

async def callback_data(bot, update: CallbackQuery):
    await bot.send_chat_action(update.message.chat.id, "typing")

    query_data = update.data

    if query_data == "start":
        buttons = Buttons.EN["START"]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_caption(
            Translation.EN["START"].format(update.from_user.mention),
            reply_markup=reply_markup,
            parse_mode="html"
        )


    elif query_data == "help":
        buttons = Buttons.EN["HELP"]
    
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_caption(
            Translation.EN["HELP"].format(update.from_user.mention),
            reply_markup=reply_markup,
            parse_mode="html"
        )


    elif query_data == "about": 
        buttons = Buttons.EN["ABOUT"]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await update.message.edit_caption(
            Translation.EN["ABOUT"],
            reply_markup=reply_markup,
            parse_mode="html"
        )


    elif query_data == "close":
        await update.message.delete()

    elif query_data == "instruct":
        await update.answer("-Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Tʜᴇ Sᴘᴇʟʟɪɴɢ Oғ Tʜᴇ Mᴏᴠɪᴇ\n-Mᴀᴋᴇ Sᴜʀᴇ Iᴛ Is Rᴇʟᴇᴀsᴇᴅ\n-Aᴠᴏɪᴅ Uɴɴᴇᴄᴇssᴀʀʏ Wᴏʀᴅs", show_alert=True)
     

async def edit_caption(bot:Client, update: CallbackQuery):

    STRING = re.findall(r"edit_c\((.+)\)", update.data)[0]

    await bot.send_chat_action(update.message.chat.id, "typing")
    await update.answer()

    if update.message.chat.type=='private':
        loading = await bot.send_message(update.message.chat.id, "◌ ◌ ◌")
        await asyncio.sleep(0.20)
        await loading.edit("● ◌ ◌")
        await asyncio.sleep(0.20)
        await loading.edit("● ● ◌")
        await asyncio.sleep(0.20)
        await loading.edit("● ● ●")
        await asyncio.sleep(0.20)
        await loading.delete()

    if STRING=="FORMAT":
        await update.message.edit(text=Translation.EN[STRING], parse_mode="html", reply_markup=InlineKeyboardMarkup(Buttons.EN[STRING]))
    elif STRING=="SPELL":
        await update.message.edit(text=Translation.EN[STRING], parse_mode="html", reply_markup=InlineKeyboardMarkup(Buttons.EN[STRING]))
    else :
        await update.message.edit(text=Translation.EN[STRING].format(update.from_user.mention), parse_mode="html", reply_markup=InlineKeyboardMarkup(Buttons.EN[STRING]), disable_web_page_preview=True)

    await bot.send_chat_action(update.message.chat.id, "cancel")
     

async def alerter(bot:Client, update: CallbackQuery):

    id, index = re.findall(r"alert\((.+)\)", update.data)[0].split("|",1)

    text = await db.get_alert(id, index)

    if not text:
        return

    await update.answer(text, show_alert=True)

async def edit_t(bot:Client, update: CallbackQuery):

    id, index = re.findall(r"edit_t\((.+)\)", update.data)[0].split("|",1)

    text, buttons = await db.get_edit(id, int(index))

    if text and buttons:

        buttons = eval(buttons)
        await update.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif text:

        await update.message.edit(text=text)

    else :

        return await update.answer("Theres Nothing Here Man...")

    await update.answer()

async def edit_m(bot:Client, update: CallbackQuery):

    id = re.findall(r"edit_m\((.+)\)", update.data)[0]

    filter = await db.get_mfilter(id)
    text = filter.get('text', 'null')
    buttons = filter.get('buttons', None)

    if text and buttons:

        buttons = eval(buttons)
        await update.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif text:

        await update.message.edit(text=text)

    else :

        return await update.answer("Theres Nothing Here Man...")

    await update.answer()

async def cb_stats(bot:Client, update:CallbackQuery):

    try:
        await update.answer("Fᴇᴛᴄʜɪɴɢ Dᴇᴛᴀɪʟs...")
        stats = await db.get_stats()
        text = f"♡ Dᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs ᴏғ Dᴏʀᴀ:-\n\nFɪʟᴇs : {stats['files']}\n\nUsᴇʀs : {stats['users']}\n\nCᴏɴɴᴇᴄᴛᴇᴅ Usᴇʀs : {stats['conn']}\n\nMᴀɴᴜᴀʟ Fɪʟᴛᴇʀs : {stats['filters']}\n\nCᴜsᴛᴏᴍɪᴢᴇᴅ Cʜᴀᴛs : {stats['chats']}"
        if update.message.text == text: return
        await update.message.edit(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏡 ʜᴏᴍᴇ 🏡", callback_data="edit_c(START)"), InlineKeyboardButton("Rᴇғʀᴇsʜ", callback_data="stats")]]),
            parse_mode='html'
        )
    except Exception as e:
        print(e)
    
async def ignore(bot:Client, update:CallbackQuery):

    await update.answer("Yᴏᴜ Hᴀᴠᴇ Hɪᴛ A Wᴀʟʟ 💥🧱🚗", show_alert=True)

async def answer_alert(bot:Client, update:CallbackQuery):

    key = re.findall(r'answer\((.+)\)', update.data)[0]

    if key=='SELECTED':
        await update.answer("Tʜɪs Hᴀs Aʟʀᴇᴀᴅʏ Bᴇᴇɴ Sᴇʟᴇᴄᴛᴇᴅ :)", show_alert=True)
    elif key=='INFO':
        await update.answer("""
        Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ :

        1. Sᴇɴᴅ ᴀ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ
        2. Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴡɪᴛʜ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ᴀɴᴅ sɪᴢᴇ ғᴏʀ ʏᴏᴜ
        3. Pʀᴇss sᴛᴀʀᴛ
        """, show_alert=True)

    elif key=="CLOSED":
        await update.answer("""
        Tʜᴇ Rᴇsᴜʟᴛs ғᴏʀ ᴛʜɪs ᴍᴏᴠɪᴇ ᴡᴀs ᴄʟᴏsᴇᴅ ᴀғᴛᴇʀ ᴀ ᴘʀᴇᴅᴇғɪɴᴇᴅ ᴛɪᴍᴇᴏᴜᴛ

        Jᴜsᴛ Asᴋ Tʜᴇ ᴍᴏᴠɪᴇ ᴀɢᴀɪɴ ᴛᴏ ɢᴇᴛ ɪᴛ
        """, show_alert=True)
    else:
        await update.answer()

def time_formatter(seconds: float) -> str:
    """ 
    humanize time 
    """
    minutes, seconds = divmod(int(seconds),60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "")
    return tmp

