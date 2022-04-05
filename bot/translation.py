#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG
import os

class Translation(object):

    EN = {
 
 "START": """<i>Hᴇʟʟᴏ {} Mʏ Nᴀᴍᴇ Is Dᴏʀᴀ I Aᴍ A Cᴏᴍᴘʟᴇᴛᴇ  AᴜᴛᴏFɪʟᴛᴇʀ + MᴀɴᴜᴀʟFɪʟᴛᴇʀ + FɪʟᴇSʜᴀʀᴇ  ʙᴏᴛ Aʟʟ Yᴏᴜ Hᴀᴠᴇ Tᴏ Dᴏ Is Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ As Aᴅᴍɪɴ \nMᴀᴋᴇ Sᴜʀᴇ Tᴏ Lᴏᴏᴋ Tʜʀᴏᴜɢʜ Mʏ Mᴀᴘ Iɴ Cᴀsᴇ Oғ Dᴏᴜʙᴛs\n\nTᴏ Usᴇ Mᴇ Iɴ PM Usᴇ Tʜᴇ <code>/connect</code> Cᴏᴍᴍᴀɴᴅ Aɴᴅ Yᴏᴜ Cᴀɴ Mᴏᴅɪғʏ AᴜᴛᴏFɪʟᴛᴇʀ Sᴇᴛᴛɪɴɢs Aɴᴅ Aᴅᴅ Mᴀɴᴜᴀʟ Fɪʟᴛᴇʀs</i>""",
 
 "HELP" : """
<i>{} Wᴇʟᴄᴏᴍᴇ Tᴏ Dᴏʀᴀ's Mᴀᴘ Iᴛ Cᴀɴ Gᴜɪᴅᴇ Yᴏᴜ Tʜʀᴏᴜɢʜ Aʟʟ Oғ Dᴏʀᴀ's Cᴏᴏʟ Fᴇᴀᴛᴜʀᴇs Aɴᴅ Hᴏᴡ Tᴏ Pʀᴏᴘᴇʀʟʏ Usᴇ Tʜᴇᴍ. Usᴇ Tʜᴇ Bᴜᴛᴛᴏɴs Bᴇʟᴏᴡ Tᴏ Nᴀᴠɪɢᴀᴛᴇ Tʜʀᴏᴜɢʜ Aʟʟ Oғ Tʜᴇ Mᴏᴅᴜʟᴇs \nYᴏᴜ Cᴀɴ Eᴀssɪʟʏ Cᴀʟʟ Mᴇ Oᴜᴛ Usɪɴɢ Tʜᴇ /map Cᴏᴍᴍᴀɴᴅ</i>""",
 
 "ABOUT" : """<b>🗲 Bot Type</b> : <i> Auto + Manual Filter + FileShare</i>
<b>🗲 Language</b> : <i><a href="https://python.org">Python 3.9.2</a></i>
<b>🗲 Library</b> : <i><a href="https://docs.pyrogram.org">Pyrogram Asyncio 1.13.0 </a></i>
<b>🗲 Server</b> : <i><a href="https://heroku.com">Heroku</a></i>
<b>🗲 DataBase</b> : <i><a href="https://mongodb.com">MongoDB</a></i>
<b>🗲 DB Driver</b> : <i><a href="https://motor.readthedocs.io">Motor Asyncio 2.5.1</a></i>
<b>🗲 IMdB Scraper</b> : <i><a href="https://pypi.org/project/IMdBPY">IMdBPY</a></i>
<b>🗲 Base Source Code</b> : <i><a href="https://github.com/AlbertEinsteinTG/Adv-Auto-Filter-Bot">Click Me</a></i>
""",

 "AF" : "<i>To Use The AutoFilter Module Simply Add The Bot To Your Group As Admin Thats it\n\n- Use The <code>/settings</code> Command To Modify AutoFilter Settings \nTo Connect The Settings Panel To PM Read The Connections Menu</i>\n Use <code>/autofilter off</code> To Disable\nUse <code>/autofilter on</code> To Enable\n",

 "MF" : '''
 <i><b>Here Are All Of The Manual FIlter Related Commands</b></i>

 -> <i>Add New Filters</i> : <code>/filter FilterWord ReplyText</code>To Add Buttons Read The Explantion On Buttons Below

 -> <i>Delete Existing Filter </i>: <code>/stop FilterText</code>

 -> <i>Veiw All Existing Filters</i> : <code>/filters</code>
 ''',
 "GLOBAL": """
 <b>Global Filter are manual filters set by bot admins themselves</b>

-> To completely disable them Go to Settings > Global Filters > Disable
-> To stop a single Global filter <code>/stopglobal Keyword</code>
-> View All the global filters with the /gfilters Command
 """,

 "BATCH" : """
 <i><b>Here's Everything Related To The Batch Module :</b></i>

 <i>(1) Add Bot To The From Channel as Admin
 (2) Send /batch Here
 (3) Forward The First Message With Quotes
 (4) Forward The Last Message Of The Batch</i>

 """,

 "CONN" : """
 <i><b>Here Is A Manual On Connections :</b></i>

 -> <i>Create A New Connection</i> : <code>/connect GroupID</code>
 -> <i>Delete Any Existing Connection</i> : <code>/disconnect</code>

 You Can Modify AutoFilter Settings And Manage Manual Filters From PM After Connecting
 """,

 "BTN" : """
 <i><b>Here Are The Basic Button Formats And Uses</b></i> :

 <i>URL Button</i> -> <code>[Button Text](url:https://example.com)</code>
 <i>Alert Button</i> -> <code>[Button Text](alert:Your Alert Text)</code>
 <i>Search Button</i> -> <code>[Button Text](search:Your Search Query)</code>
 <i>Inline Button</i> -> <code>[Button Text](inline:Your Search Query)</code>
 <i>Google Button</i> -> <code>[Button Text](google:Your Search Query)</code>

 <b>Layout Of Buttons :</b>

 To Make Buttons Appear On The Same Line Simply Type It On The Same Line To Make It Appear On The Next Line Type It On The Next Line

 Eg :
 <i>Same Line</i> ->  [Button1](url:YourURL)[Button2](alert:AlertText)

 <i>Seperate Lines</i> ->  [Button1](url:YourURL)
  Button2](alert:AlertText)
 """,
 "FORMAT": """
 <i><b>Here Are The Formatting Options Available For Manual Filters:</b></i>

 <code>{mention}</code> Mention's The User
 <code>{first_name}</code>  First Name Of The User
 <code>{last_name}</code>  Last Name Of The User
 <code>{full_name}</code>  Full Name Of The User
 <code>{username}</code>  The UserName Of The User
 <code>{id}</code>  ID Of The User

 Usage ->  Hello {mention} This Is Your Username : {username} And This Is Your ID : {id}
 """,
 "OTHER": """
 Other Commands And Weird Modules :
 
 /id ->  Reply To A Forwarded Message To Get The Original Chats ID Or Simply Get Your ID
 /json ->  Reply To A Message To Get Its Complete Json Including File IDs and Sticker IDs
 /stats -> See the DataBase stats for Dᴏʀᴀ
 """,
 "CAST":"""
<i>Just Reply To The Message Or Media You Would Like To Broadcast With <code>/broadcast</code> Buttons Will Also Be Copied

The Broadcast Feature Will Only Broadcast The Message To Users Who Are Members Of Your Group

The Command Will Work Just The Same In PM Too After Connection</i>
 """,
 "CAPTION": """
 <i><b>Use This Feature To Add A Custom Caption To Files</b></i>

 Set Caption ->  <code>/setcaption Join And Support Us</code>
 Delete Caption  ->  <code>/delcaption</code>

  <i>You Can Also Modify It From Settings Panel</i>
 """,

 "SPELL": """
 <i><b>Everything Related To The Spell Check Module When No AutoFilter Results Are Found</b></i>

 Set A New Message -> <code>/setspell YourText</code>
 Delete Existing Message -> <code>/delspell</code>

 <i>Formatting Options Are Also Available To Customize Your Message</i> :-

 {query} : The query/movie Asked By The User
 {mention} : Mention The Requester
 {name} : Name Of The User
 {id} : ID of The User

 <i>You Can Also Modify It From Settings Panel</i>
 """,

"CREDITS": """
<i><b>Heres Every Project And Person Behind This Masterpiece</i></b>

Thanks To ❤️:
• <a href='github.com/delivrance'>Dan</a> for his Beautiful <a href='docs.pyrogram.org'>Pyrogram</a> Library
• <a href='https://github.com/alberanid'>Albernaid</a> for the <a href='pypi.org/project/IMDbPY'>IMDbPY</a> library
• <a href='github.com/AlbertEinsteinTg'>AlbertEinsteinTG</a> for the <a href='github.com/AlbertEinsteinTg/Adv-auto-filter-bot-v2'>Base Repo</a>
• <a href='github.com/Arun017s'>Arun</a> for his Awesome Ideas

Tnx <a href='github.com/Jisin0'>Jisin0</a> For Putting Everything Together""",

"FSUB": """
<b>Force Group Members To Join Your Channel To Get Movie Files<b>

• Add Dora To Your Channel(IMPORTANT)
• Get The ID of the channel(Send <code>/id</code> in channel and copy)
• Open Settings > Fsub > Add New 
• Send The ID you copied earliear when the Bot asks
<b>Done!</b>

You Can Also Customize The ForceSub Message To Show in Settings > Fsub Message
""",


"AUTODEL": """
<b>Use The AutoDelete option to Close Results after a specific time</b>

Go to Settings > AutoDelete to Disable or set an AutoDelete time
"""
 }

    START_PHOTOS = [
"https://telegra.ph/file/519441afc5bf65dae75db.jpg",
"https://telegra.ph/file/d3b342fff878ce7ca52e1.jpg",
"https://telegra.ph/file/32588838b794901decb4e.jpg",
"https://telegra.ph/file/f99cc60a64a6b90812329.jpg",
"https://telegra.ph/file/d3b342fff878ce7ca52e1.jpg",
"https://telegra.ph/file/e20a11858086041780540.jpg",
"https://telegra.ph/file/31d202c0fe21f9e7a5aaf.jpg",
"https://telegra.ph/file/763283331f5359edc6d1b.jpg",
"https://telegra.ph/file/5c303c8c486f64c00626e.jpg",
"https://telegra.ph/file/0f22e6dad787ce6bde9b6.jpg",
"https://telegra.ph/file/ad5a51f55c26073917a6d.jpg"
]
    OWNER_ID = 1093541873
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))

    DORA_FIGLET = r"""
:::::::-.      ...    :::::::..    :::.     
 ;;,   `';, .;;;;;;;. ;;;;``;;;;   ;;`;;    
 `[[     [[,[[     \[[,[[[,/[[['  ,[[ '[[,  
  $$,    $$$$$,     $$$$$$$$$c   c$$$cc$$$c 
  888_,o8P'"888,_ _,88P888b "88bo,888   888,
  MMMMP"`    "YMMMMMP" MMMM   "W" YMM   YYMM
"""
    DORA_FIGLET = r"""
|   \ / _ \| _ \  /_\  
| |) | (_) |   / / _ \ 
|___/ \___/|_|_\/_/ \_\
"""
