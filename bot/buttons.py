from pyrogram.types import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup

class Buttons():

    EN = {
        "START" : [
            [InlineKeyboardButton("🅘 About 🅘", callback_data="about"),
            InlineKeyboardButton("🗺️ Map 🗺️", callback_data="help")],
            [InlineKeyboardButton("💩 My Dev 💩", url="https://t.me/J_I_S_I_N"),InlineKeyboardButton("✘ Close ✘", callback_data="close")],
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url="https://t.me/DoraFilterBot?startgroup=true")]
        ],

        "ABOUT": [
            [InlineKeyboardButton("🗺️ Map 🗺️", callback_data="help")],
            [InlineKeyboardButton("⇚ Back", callback_data="start")]
        ],

        "HELP": [
            [InlineKeyboardButton("⬐ FILTERS ⬎", callback_data="ignore")],
            [InlineKeyboardButton("Auto 🤖", callback_data="edit_c(AF)"),InlineKeyboardButton("Manual 👨‍💻", callback_data="edit_c(MF)")],
            [InlineKeyboardButton("Connections 🔗", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("Broadcast 📣", callback_data="edit_c(CAST)")],
            [InlineKeyboardButton("Batch 🗂️", callback_data="edit_c(BATCH)")],
            [InlineKeyboardButton("Others ♉", callback_data="edit_c(OTHER)")]
        ],
        "AF": [
            [InlineKeyboardButton("Connections 🔗", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ],
        "MF": [
            [InlineKeyboardButton("Buttons 🖲️", callback_data="edit_c(BTN)")],
            [InlineKeyboardButton("Formatting ✒️", callback_data="edit_c(FORMAT)")],
            [InlineKeyboardButton("Connections 🔗", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ],
        "BATCH": [
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ],
        "CONN": [
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ],
        "FORMAT": [
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(MF)")]
        ],
        "BTN": [
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(MF)")]
        ],
        "OTHER": [
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ],
        "CAST": [
            [InlineKeyboardButton("Connections 🔗", callback_data="edit_c(CONN)")],
            [InlineKeyboardButton("⇚ Back", callback_data="edit_c(HELP)")]
        ]
    }
