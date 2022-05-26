# (c) @Jisin0
from telegram import InlineKeyboardButton

class DICTIONARY(object):

    EN = {
        "START": "Hᴇʏ {mention} Usᴇ Tʜᴇ Bᴜᴛᴛᴏɴs Bᴇʟᴏᴡ Tᴏ Kɴᴏᴡ Mᴏʀᴇ Aʙᴏᴜᴛ Mᴇ ⠘⁾",
        "HELP": """
𝙷𝚘𝚠 𝚝𝚘 𝚞𝚜𝚎 𝚖𝚎 :-

𝟷) 𝙲𝚛𝚎𝚊𝚝𝚎 𝚊 𝚐𝚛𝚘𝚞𝚙
𝟸) 𝙰𝚍𝚍 𝚖𝚎 𝚝𝚑𝚎𝚛𝚎 𝚊𝚜 𝚊𝚍𝚖𝚒𝚗
𝟹) 𝙹𝚞𝚜𝚝 𝚂𝚎𝚗𝚍  𝚖𝚘𝚟𝚒𝚎 𝚗𝚊𝚖𝚎
""",
"ABOUT":"""𝙰𝚋𝚘𝚞𝚝 𝚖𝚎 𝚊𝚗𝚍 𝚑𝚘𝚠 𝙸 𝚠𝚘𝚛𝚔:-

𝙸'𝚖 𝚊 𝚙𝚎𝚛𝚜𝚘𝚗𝚊𝚕𝚒𝚣𝚎𝚍 𝚌𝚕𝚘𝚗𝚎 𝚘𝚏 @DoraFilterBot 𝚋𝚞𝚒𝚕𝚝 𝚋𝚢 <a href='tg://user?id={owner}'>𝙼𝚢 𝙼𝚊𝚜𝚝𝚎𝚛</a>

𝚆𝚊𝚗𝚗𝚊 𝚋𝚞𝚒𝚕𝚍 𝚢𝚘𝚞𝚛 𝚘𝚠𝚗 𝚋𝚘𝚝 𝚓𝚞𝚜𝚝 𝚕𝚒𝚔𝚎 𝚖𝚎...?
𝙲𝚑𝚎𝚌𝚔𝚘𝚞𝚝 𝚊 <a href='t.me/DoraFilterBot?start=clonetutorial'>𝚀𝚞𝚒𝚌𝚔 𝚅𝚒𝚍𝚎𝚘 𝚃𝚞𝚝𝚘𝚛𝚒𝚊𝚕</a> 𝚒𝚗 𝚓𝚞𝚜𝚝 𝟹 𝚎𝚊𝚜𝚢 𝚜𝚝𝚎𝚙𝚜
""",
"COMMANDS": """
𝙷𝚎𝚛𝚎 𝚒𝚜 𝚊 𝚕𝚒𝚜𝚝 𝚘𝚏 𝚖𝚢 𝚊𝚟𝚊𝚒𝚕𝚊𝚋𝚕𝚎 𝚌𝚘𝚖𝚖𝚊𝚗𝚍𝚜:

|- /start 𝙲𝚑𝚎𝚌𝚔 𝚒𝚏 𝙸'𝚖 𝚊𝚕𝚒𝚟𝚎
|- /help 𝚁𝚎𝚙𝚕𝚢 𝚊 𝚜𝚒𝚖𝚙𝚕𝚎 𝚑𝚎𝚕𝚙 𝚖𝚎𝚜𝚜𝚊𝚐𝚎
|- /about 𝙺𝚗𝚘𝚠 𝚖𝚘𝚛𝚎 𝚊𝚋𝚘𝚞𝚝 𝚖𝚎
|- /stats 𝙲𝚑𝚎𝚌𝚔 𝚖𝚢 𝚜𝚝𝚊𝚝𝚜
|- /broadcast 𝙱𝚛𝚘𝚊𝚍𝚌𝚊𝚜𝚝 𝚊 𝚖𝚎𝚜𝚜𝚊𝚐𝚎 𝚝𝚘 𝚊𝚕𝚕 𝚖𝚢 𝚞𝚜𝚎𝚛𝚜 (𝙰𝙳𝙼𝙸𝙽 𝙾𝙽𝙻𝚈)
"""
    }

class BUTTONS(object):

    EN = {
"START": [
   [InlineKeyboardButton("About", callback_data="edit(ABOUT)"),
    InlineKeyboardButton("Help", callback_data="edit(HELP)"),
    InlineKeyboardButton("Commands", callback_data='edit(COMMANDS)')]
],
"ABOUT": [
    [InlineKeyboardButton('Stats', callback_data='stats'),
    InlineKeyboardButton("Home", callback_data='edit(START)')],
    [InlineKeyboardButton("Make Your Very Own Bot", url='t.me/DoraFilterBot?start=clonetutorial')]
],
"DEFAULT": [
    [InlineKeyboardButton("H O M E", callback_data='edit(START)')]
],
'STATS': [
    [InlineKeyboardButton("About", callback_data='edit(ABOUT)'),
    InlineKeyboardButton("Refresh", callback_data='stats')]
]
}