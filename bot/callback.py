import re
import time
import asyncio
import pyrogram

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot import start_uptime, Translation, Buttons, VERIFY # pylint: disable=import-error
from bot.plugins.auto_filter import ( # pylint: disable=import-error
    FIND, 
    INVITE_LINK, 
    ACTIVE_CHATS,
    recacher,
    gen_invite_links
    )
from bot.plugins.settings import( # pylint: disable=import-error
    remove_emoji
)
from bot.database import Database # pylint: disable=import-error

db = Database()


@Client.on_callback_query(filters.regex(r"navigate\((.+)\)"), group=4)
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
    
    results = FIND.get(query).get("results")
    max_pages = FIND.get(query).get("max_pages")
    
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

    
    
    if show_invite and int(index_val) !=0 :
        
        ibuttons = []
        achatId = []
        await gen_invite_links(configs, chat_id, bot, update)
        
        for x in achats["chats"] if isinstance(achats, dict) else achats:
            achatId.append(int(x["chat_id"])) if isinstance(x, dict) else achatId.append(x)
        
        for y in INVITE_LINK.get(str(chat_id)):
            
            chat_id = int(y["chat_id"])
            
            if chat_id not in achatId:
                continue
            
            chat_name = y["chat_name"]
            invite_link = y["invite_link"]
            
            if ((len(ibuttons)%2) == 0):
                ibuttons.append(
                    [
                        InlineKeyboardButton
                            (
                                f"⚜ {chat_name} ⚜", url=invite_link
                            )
                    ]
                )

            else:
                ibuttons[-1].append(
                    InlineKeyboardButton
                        (
                            f"⚜ {chat_name} ⚜", url=invite_link
                        )
                )
            
        for x in ibuttons:
            temp_results.insert(0, x)
        ibuttons = None
        achatId = None
    
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



@Client.on_callback_query(filters.regex(r"settings"), group=4)
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




@Client.on_callback_query(filters.regex(r"warn\((.+)\)"), group=4)
async def cb_warn(bot, update: CallbackQuery):
    """
    A Callback Funtion For Acknowledging User's About What Are They Upto
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    chat_name = chat_name.encode('ascii', 'ignore').decode('ascii')[:35]
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return
    
    channel_id, channel_name, action = re.findall(r"warn\((.+)\)", query_data)[0].split("|", 2)
    
    if action == "connect":
        text=f"<i>Are You Sure You Want To Enable Connection With</i> <code>{channel_name}</code><i>..???</i>\n"
        text+=f"\n<i>This Will Show File Links From</i> <code>{channel_name}</code> <i>While Showing Results</i>..."
    
    elif action == "disconnect":
        text=f"<i>Are You Sure You Want To Disable</i> <code>{channel_name}</code> <i>Connection With The Group???....</i>\n"
        text+=f"\n<i>The DB Files Will Still Be There And You Can Connect Back To This Channel Anytime From Settings Menu Without Adding Files To DB Again...</i>\n"
        text+=f"\n<i>This Disabling Just Hide Results From The Filter Results...</i>"
    
    elif action == "c_delete":
        text=f"<i>Are You Sure You Want To Disconnect</i> <code>{channel_name}</code> <i>From This Group??</i>\n"
        text+=f"\n<i><b>This Will Delete Channel And All Its Files From DB Too....!!</b></i>\n"
        text+=f"\nYou Need To Add Channel Again If You Need To Shows It Result..."
        
    
    elif action=="f_delete":
        text=f"<i>Are You Sure That You Want To Clear All Filter From This Chat</i> <code>{channel_name}</code><i>???</i>\n"
        text+=f"\n<i>This Will Erase All Files From DB..</i>"
        
    buttons = [
        [
            InlineKeyboardButton
                (
                    "Yes", callback_data=f"{action}({channel_id}|{channel_name})"
                ), 
            
            InlineKeyboardButton
                (
                    "No", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"channel_list\((.+)\)"), group=4)
async def cb_channel_list(bot, update: CallbackQuery):    
    """
    A Callback Funtion For Displaying All Channel List And Providing A Menu To Navigate
    To Every COnnect Chats For Furthur Control
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    chat_name = chat_name.encode('ascii', 'ignore').decode('ascii')[:35]
    user_id = update.from_user.id
    
    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return

    if user_id not in VERIFY.get(str(chat_id)):
        return
        
    chat_id =  re.findall(r"channel_list\((.+)\)", query_data)[0]
    
    text = "<i>Semms Like You Dont Have Any Channel Connected...</i>\n\n<i>Connect To Any Chat To Continue With This Settings...</i>"
    
    db_list = await db.find_chat(int(chat_id))
    
    channel_id_list = []
    channel_name_list = []
    
    if db_list:
        for x in db_list["chat_ids"]:
            channel_id = x["chat_id"]
            channel_name = x["chat_name"]
            
            try:
                if (channel_id == None or channel_name == None):
                    continue
            except:
                break
            
            channel_name = remove_emoji(channel_name).encode('ascii', 'ignore').decode('ascii')[:35]
            channel_id_list.append(channel_id)
            channel_name_list.append(channel_name)
        
    buttons = []

    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close ✘", callback_data="close"
                )
        ]
    ) 

    if channel_name_list:
        
        text=f"<i>List Of Connected Channels With <code>{chat_name}</code> With There Settings..</i>\n"
    
        for x in range(1, (len(channel_name_list)+1)):
            text+=f"\n<code>{x}. {channel_name_list[x-1]}</code>\n"
    
        text += "\nChoose Appropriate Buttons To Navigate Through Respective Channels"
    
        
        btn_key = [
            "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", 
            "1️⃣1️⃣", "1️⃣2️⃣", "1️⃣3️⃣", "1️⃣4️⃣", "1️⃣5️⃣", "1️⃣6️⃣", "1️⃣7️⃣", 
            "1️⃣8️⃣", "1️⃣9️⃣", "2️⃣0️⃣" # Just In Case 😂🤣
        ]
    
        for i in range(1, (len(channel_name_list) + 1)): # Append The Index Number of Channel In Just A Single Line
            if i == 1:
                buttons.insert(0,
                    [
                    InlineKeyboardButton
                        (
                            btn_key[i-1], callback_data=f"info({channel_id_list[i-1]}|{channel_name_list[i-1]})"
                        )
                    ]
                )
        
            else:
                buttons[0].append(
                    InlineKeyboardButton
                        (
                            btn_key[i-1], callback_data=f"info({channel_id_list[i-1]}|{channel_name_list[i-1]})"
                        )
                )
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
            text = text,
            reply_markup=reply_markup,
            parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"info\((.+)\)"), group=4)
async def cb_info(bot, update: CallbackQuery):
    """
    A Callback Funtion For Displaying Details Of The Connected Chat And Provide
    Ability To Connect / Disconnect / Delete / Delete Filters of That Specific Chat
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return

    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"info\((.+)\)", query_data)[0].split("|", 1)
    
    f_count = await db.cf_count(chat_id, int(channel_id)) 
    active_chats = await db.find_active(chat_id)

    if active_chats: # Checks for active chats connected to a chat
        dicts = active_chats["chats"]
        db_cids = [ int(x["chat_id"]) for x in dicts ]
        
        if int(channel_id) in db_cids:
            active_chats = True
            status = "Connected"
            
        else:
            active_chats = False
            status = "Disconnected"
            
    else:
        active_chats = False
        status = "Disconnected"

    text=f"<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>{status}</code>\n"


    if active_chats:
        buttons = [
                    [
                        InlineKeyboardButton
                            (
                                "🚨 Disconnect 🚨", callback_data=f"warn({channel_id}|{channel_name}|disconnect)"
                            ),
                        
                        InlineKeyboardButton
                            (
                                "Delete ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                            )
                    ]
        ]

    else:
        buttons = [ 
                    [
                        InlineKeyboardButton
                            (
                                "💠 Connect 💠", callback_data=f"warn({channel_id}|{channel_name}|connect)"
                            ),
                        
                        InlineKeyboardButton
                            (
                                "Delete ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                            )
                    ]
        ]

    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "Delete Filters ⚠", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⇚ Back", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )

    reply_markup = InlineKeyboardMarkup(buttons)
        
    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"^connect\((.+)\)"), group=4)
async def cb_connect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat Active Chat Which Will
    Make The Bot To Fetch Results From This Channel Too
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return

    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    f_count = await db.cf_count(chat_id, channel_id)
    
    add_active = await db.update_active(chat_id, channel_id, channel_name)
    
    if not add_active:
        await update.answer(f"{channel_name} Is Aldready in Active Connection", show_alert=True)
        return

    text= f"<i>Sucessfully Connected To</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>Connected</code>\n"

    buttons = [
                [
                    InlineKeyboardButton
                        (
                            "🚨 Disconnect 🚨", callback_data=f"warn({channel_id}|{channel_name}|disconnect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "Delete ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "Delete Filters ⚠", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⇚ Back", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    await recacher(chat_id, False, True, bot, update)
    
    reply_markup = InlineKeyboardMarkup(buttons)
        
    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"disconnect\((.+)\)"), group=4)
async def cb_disconnect(bot, update: CallbackQuery):
    """
    A Callback Funtion Helping The user To Make A Chat inactive Chat Which Will
    Make The Bot To Avoid Fetching Results From This Channel
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return

    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"connect\((.+)\)", query_data)[0].split("|", 1)
    
    f_count = await db.cf_count(chat_id, int(channel_id))
    
    remove_active = await db.del_active(chat_id, int(channel_id))
    
    if not remove_active:
        await update.answer("Couldnt Full Fill YOur Request...\n Report This @CrazyBotszGrp Along With Bot's Log", show_alert=True)
        return
    
    text= f"<i>Sucessfully Disconnected From</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Info About <b>{channel_name}</b></i>\n"
    text+=f"\n<i>Channel Name:</i> <code>{channel_name}</code>\n"
    text+=f"\n<i>Channel ID:</i> <code>{channel_id}</code>\n"
    text+=f"\n<i>Channel Files:</i> <code>{f_count}</code>\n"
    text+=f"\n<i>Current Status:</i> <code>Disconnected</code>\n"
    
    buttons = [ 
                [
                    InlineKeyboardButton
                        (
                            "💠 Connect 💠", callback_data=f"warn({channel_id}|{channel_name}|connect)"
                        ),
                    
                    InlineKeyboardButton
                        (
                            "Delete ❌", callback_data=f"warn({channel_id}|{channel_name}|c_delete)"
                        )
                ]
    ]
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "Delete Filters ⚠", callback_data=f"warn({channel_id}|{channel_name}|f_delete)"
                    )
            ]
    )
    
    buttons.append(
            [
                InlineKeyboardButton
                    (
                        "⇚ Back", callback_data=f"channel_list({chat_id})"
                    )
            ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await recacher(chat_id, False, True, bot, update)

    await update.message.edit_text(
            text, reply_markup=reply_markup, parse_mode="html"
        )



@Client.on_callback_query(filters.regex(r"c_delete\((.+)\)"), group=4)
async def cb_channel_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Channel Connection From A Group Chat History
    Along With All Its Filter Files
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"c_delete\((.+)\)", query_data)[0].split("|", 1)
    channel_id = int(channel_id)
    
    c_delete = await db.del_chat(chat_id, channel_id)
    a_delete = await db.del_active(chat_id, channel_id) # pylint: disable=unused-variable
    f_delete = await db.del_filters(chat_id, channel_id)

    if (c_delete and f_delete ):
        text=f"<code>{channel_name} [ {channel_id} ]</code> Has Been Sucessfully Deleted And All Its Files Were Cleared From DB...."

    else:
        text=f"<i>Couldn't Delete Channel And All Its Files From DB Sucessfully....</i>\n<i>Please Try Again After Sometimes...Also Make Sure To Check The Logs..!!</i>"
        await update.answer(text=text, show_alert=True)

    buttons = [
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"channel_list({chat_id})"
                ),
                
            InlineKeyboardButton
                (
                    "Close ✘", callback_data="close"
                )
        ]
    ]

    await recacher(chat_id, True, True, bot, update)
    
    reply_markup=InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"f_delete\((.+)\)"), group=4)
async def cb_filters_delete(bot, update: CallbackQuery):
    """
    A Callback Funtion For Delete A Specific Channel's Filters Connected To A Group
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    channel_id, channel_name = re.findall(r"f_delete\((.+)\)", query_data)[0].split("|", 1)

    f_delete = await db.del_filters(chat_id, int(channel_id))

    if not f_delete:
        text="<b><i>Oops..!!</i></b>\n\nEncountered Some Error While Deleteing Filters....\nPlease Check The Logs...."
        await update.answer(text=text, show_alert=True)
        return

    text =f"All Filters Of <code>{channel_id}[{channel_name}]</code> Has Been Deleted Sucessfully From My DB.."

    buttons=[
        [
            InlineKeyboardButton
                (
                    "Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close", callback_data="close"
                )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )
    


@Client.on_callback_query(filters.regex(r"types\((.+)\)"), group=4)
async def cb_types(bot, update: CallbackQuery):
    """
    A Callback Funtion For Changing The Result Types To Be Shown In While Sending Results
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id = re.findall(r"types\((.+)\)", query_data)[0]
    
    _types = await db.find_chat(int(chat_id))
    
    text=f"<i>Filter Types Enabled/Disbled In <code>{chat_name}</code></i>\n"
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    buttons = []
    
    if vid:
        text+="\n<i><b>Video Index:</b> Enabled</i>\n"
        v_e = "✅"
        vcb_data = f"toggle({chat_id}|video|False)"
    
    else:
        text+="\n<i><b>Video Index:</b> Disabled</i>\n"
        v_e="❎"
        vcb_data = f"toggle({chat_id}|video|True)"

    if doc:
        text+="\n<i><b>Document Index:</b> Enabled</i>\n"
        d_e = "✅"
        dcb_data = f"toggle({chat_id}|document|False)"

    else:
        text+="\n<i><b>Document Index:</b> Disabled</i>\n"
        d_e="❎"
        dcb_data = f"toggle({chat_id}|document|True)"

    if aud:
        text+="\n<i><b>Audio Index:</b> Enabled</i>\n"
        a_e = "✅"
        acb_data = f"toggle({chat_id}|audio|False)"

    else:
        text+="\n<i><b>Audio Index:</b> Disabled</i>\n"
        a_e="❎"
        acb_data = f"toggle({chat_id}|audio|True)"

    
    text+="\n<i>Below Buttons Will Toggle Respective Media Types As Enabled Or Disabled....\n</i>"
    text+="<i>This Will Take Into Action As Soon As You Change Them....</i>"
    
    buttons.append([InlineKeyboardButton(f"Video Index: {v_e}", callback_data=vcb_data)])
    buttons.append([InlineKeyboardButton(f"Audio Index: {a_e}", callback_data=acb_data)])
    buttons.append([InlineKeyboardButton(f"Document Index: {d_e}", callback_data=dcb_data)])
    
    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"toggle\((.+)\)"), group=4)
async def cb_toggle(bot, update: CallbackQuery):
    """
    A Callback Funtion Support handler For types()
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id, types, val = re.findall(r"toggle\((.+)\)", query_data)[0].split("|", 2)
    
    _types = await db.find_chat(int(chat_id))
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    if types == "video":
        vid = True if val=="True" else False
    elif types == "audio":
        aud = True if val=="True" else False
    elif types == "document":
        doc = True if val=="True" else False
    
        
    settings = {
        "video": vid,
        "audio": aud,
        "document": doc
    }

    process = await db.update_settings(chat_id, settings)
    
    if process:
        await update.answer(text="Filter Types Updated Sucessfully", show_alert=True)
    
    else:
        text="Something Wrong Please Check Bot Log For More Information...."
        await update.answer(text, show_alert=True)
        return
    
    _types = await db.find_chat(int(chat_id))
    
    text =f"<i>Filter Types Enabled In <code>{update.message.chat.title}</code></i>\n"
    
    _types = _types["types"]
    vid = _types["video"]
    doc = _types["document"]
    aud = _types["audio"]
    
    buttons = []
    
    if vid:
        text+="\n<i><b>Video Index:</b> Enabled</i>\n"
        v_e = "✅"
        vcb_data = f"toggle({chat_id}|video|False)"
    
    else:
        text+="\n<i><b>Video Index:</b> Disabled</i>\n"
        v_e="❎"
        vcb_data = f"toggle({chat_id}|video|True)"

    if doc:
        text+="\n<i><b>Document Index:</b> Enabled</i>\n"
        d_e = "✅"
        dcb_data = f"toggle({chat_id}|document|False)"

    else:
        text+="\n<i><b>Document Index:</b> Disabled</i>\n"
        d_e="❎"
        dcb_data = f"toggle({chat_id}|document|True)"

    if aud:
        text+="\n<i><b>Audio Index:</b> Enabled</i>\n"
        a_e = "✅"
        acb_data = f"toggle({chat_id}|audio|False)"

    else:
        text+="\n<i><b>Audio Index:</b> Disabled</i>\n"
        a_e="❎"
        acb_data = f"toggle({chat_id}|audio|True)"

    
    text+="\n<i>Below Buttons Will Toggle Respective Media Types As Enabled Or Disabled....\n</i>"
    text+="<i>This Will Take Into Action As Soon As You Change Them....</i>"
    
    buttons.append([InlineKeyboardButton(f"Video Index : {v_e}", callback_data=vcb_data)])
    buttons.append([InlineKeyboardButton(f"Audio Index : {a_e}", callback_data=acb_data)])
    buttons.append([InlineKeyboardButton(f"Document Index : {d_e}", callback_data=dcb_data)])
    
    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    )
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"config\((.+)\)"), group=4)
async def cb_config(bot, update: CallbackQuery):
    """
    A Callback Funtion For Chaning The Number Of Total Pages / 
    Total Results / Results Per pages / Enable or Diable Invite Link /
    Enable or Disable PM File Chat
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Thats A Restricted Area Mahn", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    chat_id = re.findall(r"config\((.+)\)", query_data)[0]
    
    settings = await db.find_chat(int(chat_id))
    
    mp_count = settings["configs"]["max_pages"]
    mf_count = settings["configs"]["max_results"]
    mr_count = settings["configs"]["max_per_page"]
    show_invite = settings["configs"]["show_invite_link"]
    pm_file_chat  = settings["configs"].get("pm_fchat", False)
    accuracy_point = settings["configs"].get("accuracy", 0.70)
    
    text=f"<i><b>Configure Your <u><code>{chat_name}</code></u> Group's Filter Settings...</b></i>\n"
    
    text+=f"\n<i>{chat_name}</i> Current Settings:\n"

    text+=f"\n - Max Filter: <code>{mf_count}</code>\n"
    
    text+=f"\n - Max Pages: <code>{mp_count}</code>\n"
    
    text+=f"\n - Max Filter Per Page: <code>{mr_count}</code>\n"

    text+=f"\n - Accuracy Percentage: <code>{accuracy_point}</code>\n"
    
    text+=f"\n - Show Invitation Link: <code>{show_invite}</code>\n"
    
    text+=f"\n - Provide File In Bot PM: <code>{pm_file_chat}</code>\n"
    
    text+="\nAdjust Above Value Using Buttons Below... "
    buttons=[
        [
            InlineKeyboardButton
                (
                    "Filter Per Page", callback_data=f"mr_count({mr_count}|{chat_id})"
                ), 
    
            InlineKeyboardButton
                (
                    "Max Pages",       callback_data=f"mp_count({mp_count}|{chat_id})"
                )
        ]
    ]


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "Total Filter Count", callback_data=f"mf_count({mf_count}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [                
             InlineKeyboardButton
                (
                    "Show Invite Links", callback_data=f"show_invites({show_invite}|{chat_id})"
                ),

            InlineKeyboardButton
                (
                    "Bot File Chat", callback_data=f"inPM({pm_file_chat}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "Result's Accuracy", callback_data=f"accuracy({accuracy_point}|{chat_id})"
                )
        ]
    )


    buttons.append(
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data=f"settings"
                )
        ]
    )
    
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"mr_count\((.+)\)"), group=4)
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



@Client.on_callback_query(filters.regex(r"mp_count\((.+)\)"), group=4)
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



@Client.on_callback_query(filters.regex(r"mf_count\((.+)\)"), group=4)
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



@Client.on_callback_query(filters.regex(r"show_invites\((.+)\)"), group=4)
async def cb_show_invites(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling Invite Link Buttons
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    value, chat_id = re.findall(r"show_invites\((.+)\)", query_data)[0].split("|", 1)
    
    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "Disable ❌", callback_data=f"set(showInv|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Back ⇚", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "Enable ✔", callback_data=f"set(showInv|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Back ⇚", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>This Config Will Help You To Show Invitation Link Of All Active Chats Along With The Filter Results For The Users To Join.....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"inPM\((.+)\)"), group=4)
async def cb_pm_file(bot, update: CallbackQuery):
    """
    A Callback Funtion For Enabling Or Diabling File Transfer Through Bot PM
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    user_id = update.from_user.id

    if user_id not in (Translation.OWNER_ID,):
        await bot.send_message(Translation.OWNER_ID, f"This Bitch {update.from_user.mention} Trying To Use A Banned Callback")
        await update.answer("Kooduthal Velachchil Edukkalle Myre 😏", show_alert=True)
        return
    
    if user_id not in VERIFY.get(str(chat_id)):
        return

    value, chat_id = re.findall(r"inPM\((.+)\)", query_data)[0].split("|", 1)

    value = True if value=="True" else False
    
    if value:
        buttons= [
            [
                InlineKeyboardButton
                    (
                        "Disable ❎", callback_data=f"set(inPM|False|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Back ⇚", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    else:
        buttons =[
            [
                InlineKeyboardButton
                    (
                        "Enable ✅", callback_data=f"set(inPM|True|{chat_id}|{value})"
                    )
            ],
            [
                InlineKeyboardButton
                    (
                        "Back ⇚", callback_data=f"config({chat_id})"
                    )
            ]
        ]
    
    text=f"<i>This Config Will Help You To Enable/Disable File Transfer Through Bot PM Without Redirecting Them To Channel....</i>"
    
    reply_markup=InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text,
        reply_markup=reply_markup,
        parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"accuracy\((.+)\)"), group=4)
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



@Client.on_callback_query(filters.regex(r"set\((.+)\)"), group=4)
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



@Client.on_callback_query(filters.regex(r"status\((.+)\)"), group=4)
async def cb_status(bot, update: CallbackQuery):
    """
    A Callback Funtion For Showing Overall Status Of A Group
    """
    global VERIFY
    query_data = update.data
    chat_id = update.message.chat.id
    chat_name = remove_emoji(update.message.chat.title)
    user_id = update.from_user.id
    
    if user_id not in (Translation.OWNER_ID,):
        return
    
    chat_id = re.findall(r"status\((.+)\)", query_data)[0]
    
    total_filters, total_chats, total_achats = await db.status(chat_id)
    
    text = f"<b><i>Status Of {chat_name}</i></b>\n"
    text += f"\n<b>Total Connected Chats:</b> <code>{total_chats}</code>\n"
    text += f"\n<b>Total Active Chats:</b> <code>{total_achats}</code>\n"
    text += f"\n<b>Total Filters:</b> <code>{total_filters}</code>"
    
    buttons = [
        [
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close ✘", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"about\((.+)\)"), group=4)
async def cb_about(bot, update: CallbackQuery):
    """
    A Callback Funtion For Showing About Section In Bot Setting Menu
    """
    global VERIFY
    chat_id = update.message.chat.id
    user_id = update.from_user.id
    
    if user_id not in (Translation.OWNER_ID,):
        return

    text=f"<i><u>Bot's Status</u></i>\n"
    text+=f"\n<b><i>Bot's Uptime:</i></b> <code>{time_formatter(time.time() - start_uptime)}</code>\n"
    text+=f"\n<b><i>Bot Funtion:</i></b> <i>Auto Filter Files</i>\n"
    text+=f"""\n<b><i>Bot Support:</i></b> <a href="https://t.me/CrazyBotszGrp">@CrazyBotszGrp</a>\n"""
    text+="""\n<b><i>Source Code:</i></b> <a href="https://github.com/CrazyBotsz/Adv-Filter-Bot-V2">Source</a>"""

    buttons = [
        [
            InlineKeyboardButton
                (
                    "My Dev ⚡", url="https://t.me/AlbertEinstein_TG"
                ),
                
            InlineKeyboardButton
                (
                    "⇚ Back", callback_data="settings"
                )
        ],
        [
            InlineKeyboardButton
                (
                    "Close ✘", callback_data="close"
                )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.edit_text(
        text, reply_markup=reply_markup, parse_mode="html"
    )



@Client.on_callback_query(filters.regex(r"^(start|help|about|close|instruct)$"), group=4)
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
     

@Client.on_callback_query(filters.regex(r"edit_c\((.+)\)"), group=4)
async def edit_caption(bot:Client, update: CallbackQuery):

    STRING = re.findall(r"edit_c\((.+)\)", update.data)[0]

    await bot.send_chat_action(update.message.chat.id, "typing")
    await update.answer()

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
     

@Client.on_callback_query(filters.regex(r"alert\((.+)\)"), group=4)
async def alerter(bot:Client, update: CallbackQuery):

    id, index = re.findall(r"alert\((.+)\)", update.data)[0].split("|",1)

    text = await db.get_alert(id, index)

    if not text:
        return

    await update.answer(text, show_alert=True)
@Client.on_callback_query(filters.regex(r"edit_t\((.+)\)"), group=4)
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

@Client.on_callback_query(filters.regex(r"edit_m\((.+)\)"), group=4)
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

@Client.on_callback_query(filters.regex("stats"), group=4)
async def cb_stats(bot:Client, update:CallbackQuery):

    try:
        await update.answer("Fᴇᴛᴄʜɪɴɢ Dᴇᴛᴀɪʟs...")
        stats = await db.get_stats()
        await update.message.edit(
            f"<b>♡ Dᴀᴛᴀʙᴀsᴇ sᴛᴀᴛs ᴏғ Dᴏʀᴀ:-</b>\n\nFɪʟᴇs : {stats['files']}\nUsᴇʀs : {stats['users']}\nCᴏɴɴᴇᴄᴛᴇᴅ Usᴇʀs : {stats['conn']}\nMᴀɴᴜᴀʟ Fɪʟᴛᴇʀs : {stats['filters']}\nCᴜsᴛᴏᴍɪᴢᴇᴅ Cʜᴀᴛs : {stats['chats']}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏡 ʜᴏᴍᴇ 🏡", callback_data="edit_c(START)"), InlineKeyboardButton("Rᴇғʀᴇsʜ", callback_data="stats")]]),
            parse_mode='html'
        )
    except Exception as e:
        print(e)
    
@Client.on_callback_query(filters.regex("ignore"), group=4)
async def ignore(bot:Client, update:CallbackQuery):

    await update.answer("Yᴏᴜ Hᴀᴠᴇ Hɪᴛ A Wᴀʟʟ 💥🧱🚗", show_alert=True)

@Client.on_callback_query(filters.regex(r'answer\((.+)\)'))
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

