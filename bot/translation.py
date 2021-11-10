#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

class Translation(object):

    EN = {
 
 "START": """<i><b>Hello {} My Name Is Dora I Am A Complete  AutoFilter + ManualFilter + FileShare  bot All You Have To Do Is Add Me To Your Group As Admin \nMake Sure To Look Through My Map In Case Of Doubts\n\nTo Use Me In PM Use The <code>/connect</code> Command And You Can Modify AutoFilter Settings And Add Manual Filters.</b>
</i>""",
 
 "HELP" : """
<b>Hey {} My Name is Map I Can Guide You Through All Of Dora's Cool Features And How To Properly Use Them. Use The Buttons Below To Navigate Through All Of The Modules \nYou Can Eassily Call Me Out Using The /map Command</b>
""",
 
 "ABOUT" : """<b>➥ Name</b> : <code> Auto Filter Bot</code>
 
<b>➥ Base Dev</b> : <b><i><a href="https://t.me/AlbertEinstein_TG">AlbertEinstein_TG</a></i></b>
<b>➥ Main Dev</b> : <b><i><a href="https://t.me/J_I_S_I_N">MrPurple902</a></i></b>
<b>➥ Language</b> : <i><a href="https://python.org">Python 3.9.2</a></i>
<b>➥ Library</b> : <i><a href="https://docs.pyrogram.org">Pyrogram Asyncio 1.13.0 </a></i>
<b>➥ Base Source Code</b> : <i><a href="https://github.com/AlbertEinsteinTG/Adv-Auto-Filter-Bot">Click Me</a></i>
<b>➥ Server</b> : <i><a href="https://heroku.com">Heroku</a></i>
<b>➥ DataBase</b> : <i><a href="https://mongodb.com">MongoDB</a></i>
""",

 "AF" : "<b>To Use The AutoFilter Module Simply Add The Bot To Your Group As Admin Thats it/n/n- Use The <code>/settings</code> Command To Modify AutoFilter Settings \nTo Connect The Settings Panel To PM Read The Connections Menu</b>",

 "MF" : '''
 <i><b>Here Are All Of The Manual FIlter Related Commands</b></i>

 -> <i>Add New Filters</i> : <code>/filter FilterWord ReplyText</code>To Add Buttons Read The Explantion On Buttons Below

 -> <i>Delete Existing Filter </i>: <code>/stop FilterText</code>

 -> <i>Veiw All Existing Filters</i> : <code>/filters</code>
 ''',

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

 <b>Layout Of Buttons :</b>

 To Make Buttons Appear On The Same Line Simply Type It On The Same Line To Make It Appear On The Next Line Type It On The Next Line

 Eg :
 <i>Same Line</i> ->  [Button1](url:YourURL)[Button2](alert:AlertText)

 <i>Seperate Lines</i> ->  [Button1](url:YourURL)
  [Button2](alert:AlertText)
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
 /json ->  Rply To A Message To Get Its Complette Json Includinf File IDs and Sticker IDs
 """,
 "CAST":"""
<i>Just Reply To The Message Or Media You Would Like To Broadcast With <code>/broadcast</code> Buttons Will Also Be Copied

The Broadcast Feature Will Only Broadcast The Message To Users Who Are Members Of Your Group

The Command Will Work Just The Same In PM Too After Connection</i>
 """
 }

    START_PHOTOS = ["https://telegra.ph/file/ffe4162578924f7583d6a.jpg",

"https://telegra.ph/file/888eb5675668f59aba9e6.jpg",

"https://telegra.ph/file/d79b681ce71e6d749bd03.jpg",

"https://telegra.ph/file/ea99ee6f82be0b9582d4d.jpg",

"https://telegra.ph/file/564178c3770cd264a9ad3.jpg",

"https://telegra.ph/file/24735799583ce411fc698.jpg",

"https://telegra.ph/file/a50a1f52db516449fe672.jpg",

"https://telegra.ph/file/f4ca759b7abaafa74e86d.jpg",

"https://telegra.ph/file/94de07b2713f94be57702.jpg",

"https://telegra.ph/file/ff35287f729d667efa2c7.jpg",

"https://telegra.ph/file/d0c5347f93247bcc7e214.jpg",

"https://telegra.ph/file/bcb06af3806e64ffeebbf.jpg",

"https://telegra.ph/file/98fb833c7b7ae1c65f198.jpg"]