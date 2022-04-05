from pyrogram.types import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup

class Buttons():

    EN = {
        "START" : [
            [InlineKeyboardButton("ꖜ 𝙰𝚋𝚘𝚞𝚝 ꖜ", callback_data="edit_c(ABOUT)"),InlineKeyboardButton("⏣ Mᴀᴘ ⏣", callback_data="edit_c(HELP)")],
            [InlineKeyboardButton("♡ Sᴜᴘᴘᴏʀᴛ Tᴇᴀᴍ ♡", url="https://t.me/DoraSupportTeam"),InlineKeyboardButton("¿ 𝚂𝚎𝚊𝚛𝚌𝚑 ?", switch_inline_query_current_chat="")],
            [InlineKeyboardButton("⨭ Aᴅᴅ ᴍᴇ ᴛᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⨮", url="https://t.me/DoraFilterBot?startgroup=true")]
        ],

        "ABOUT": [
            [InlineKeyboardButton("⸙ Cʀᴇᴅɪᴛs ⸙", callback_data="edit_c(CREDITS)"), InlineKeyboardButton("⏣ Mᴀᴘ ⏣️", callback_data="edit_c(HELP)"), InlineKeyboardButton("⌭ Sᴛᴀᴛs ⌭", callback_data='stats')],
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(START)")]
        ],

        "HELP": [
            [InlineKeyboardButton("⎔ Aᴜᴛᴏ Fɪʟᴛᴇʀ ⎔", callback_data="edit_c(AF)"), InlineKeyboardButton("⎎ Mᴀɴᴜᴀʟ Fɪʟᴛᴇʀs ⎎", callback_data="edit_c(MF)"), InlineKeyboardButton("꩜ Gʟᴏʙᴀʟ Fɪʟᴛᴇʀs ꩜", callback_data="edit_c(MF)")],
            [InlineKeyboardButton("⎙ Bᴀᴛᴄʜ ⎙️", callback_data="edit_c(BATCH)"), InlineKeyboardButton("⌬ Cᴏɴɴᴇᴄᴛɪᴏɴ ⌬", callback_data="edit_c(CONN)"), InlineKeyboardButton("⌥ Bʀᴏᴀᴅᴄᴀsᴛ ⌥", callback_data="edit_c(CAST)")],
            [InlineKeyboardButton("« AᴜᴛᴏDᴇʟᴇᴛᴇ »️", callback_data='edit_c(AUTODEL)'), InlineKeyboardButton("ꔮ Cᴀᴘᴛɪᴏɴ ꔮ", callback_data="edit_c(CAPTION)"), InlineKeyboardButton("✎ Sᴘᴇʟʟᴄʜᴇᴄᴋ ✎️", callback_data='edit_c(SPELL)')],
            [InlineKeyboardButton("⏣ Oᴛʜᴇʀ ⏣", callback_data="edit_c(OTHER)"), InlineKeyboardButton("⌤ Hᴏᴍᴇ ⌤", callback_data="edit_c(START)")]
        ],
        "AF": [
            [InlineKeyboardButton("⌬ Cᴏɴɴᴇᴄᴛɪᴏɴ ⌬", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "MF": [
            [InlineKeyboardButton("⎉ Bᴜᴛᴛᴏɴs ⎉️", callback_data="edit_c(BTN)")],
            [InlineKeyboardButton("⎚ Fᴏʀᴍᴀᴛᴛɪɴɢ ⎚️", callback_data="edit_c(FORMAT)")],
            [InlineKeyboardButton("⌬ Cᴏɴɴᴇᴄᴛɪᴏɴ ⌬", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "BATCH": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "CREDITS": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(ABOUT)")]
        ],
        "AUTODEL": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "CONN": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "FORMAT": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(MF)")]
        ],
        "BTN": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(MF)")]
        ],
        "OTHER": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "CAST": [
            [InlineKeyboardButton("⌬ Cᴏɴɴᴇᴄᴛɪᴏɴ ⌬", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ],
        "CAPTION": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]],
        "SPELL": [
            [InlineKeyboardButton("Bᴀᴄᴋ ⎆", callback_data="edit_c(HELP)")]
        ]
    }
