import re
import asyncio
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, PeerIdInvalid, ChannelInvalid

from pyrogram.types.bots_and_keyboards.callback_query import CallbackQuery
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters

from bot.database import Database 
from bot import VERIFY

db = Database()

@Client.on_callback_query(filters.regex(r'fix\((.+)\)'))
async def fix_value(bot:Client, update:CallbackQuery):

    key, action, group_id = re.findall(r'fix\((.+)\)', update.data)[0].split('|',2)
    await update.answer()
    group_id = int(group_id)

    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)

    if action=='on':

        await db.set_main(group_id, key, True)

    elif action=='off':

        await db.del_main(group_id, key)

    elif action=='def':

        await db.set_main(group_id, key, 'def')

    else :

        ask = await bot.send_message(update.message.chat.id, "``Ok Now Send Me The New Value...\n\nTo Abort This Process Send /cancel``", parse_mode='md')
        response:Message = await bot.listen(update.message.chat.id, filters.user(update.from_user.id), timeout=300)

        if not response:
            return
        if response.text.startswith('/cancel'):
            await ask.edit_text("`Aborting Process...`", parse_mode='md')
            await asyncio.sleep(3)
            await ask.delete()
            return

        if key=='fsub':

            try:
                chat_id = int(response.text)
                chat = await bot.get_chat(chat_id)
                title = chat.title
                id = chat.id
                result = dict(
                    id=id,
                    title=title
                )
            except TypeError:
                return await response.reply_text("That Doesnt Look Like A Valid ChatID...")
            except PeerIdInvalid:
                return await response.reply_text("Oh no looks Like I'm Not A Member Of This Channel Please Add Me There First...")
            except ChannelInvalid:
                return await response.reply_text("Oh no looks Like I'm Not A Member Of This Channel Please Add Me There First...")

        else :

            result = response.text

        await db.set_main(group_id, key, result)
        await ask.delete()
    
    await update.message.edit_text("Your Request Was Updated Successfully...", reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ]]))


@Client.on_callback_query(filters.regex(r"fsub_msg\((.+)\)"), group=4)
async def toggle_fsubmsg(bot: Client, update:CallbackQuery):

    group_id = re.findall(r'fsub_msg\((.+)\)', update.data)[0]
    user_id = update.from_user.id

    member = await bot.get_chat_member(group_id, user_id)
    if not member.status in ('administrator','creator'):
        return await update.answer('Nice Try Kid xD', show_alert=True)

    buttons = [
        [InlineKeyboardButton("Default", callback_data=f"fix(fsub_msg|off|{group_id})"),
        InlineKeyboardButton("Set New", callback_data=f"fix(fsub_msg|idk|{group_id})")
        ]
    ]

    await update.message.edit_text("Use The Buttons Below To Set A Custom Message To Show Someone Who Hasn't Joined The Fsub Channel...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'af\((.+)\)'), group=4)
async def toggle_af(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'af\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    user_id = update.from_user.id
    chat_id = update.message.chat.id

    member = await bot.get_chat_member(group_id, user_id)
    if not member.status in ('administrator','creator'):
        return await update.answer('Nice Try Kid xD', show_alert=True)

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(af|off|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Enable',  callback_data=f'fix(af|on|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Toggle AutoFilter On/Off ...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'size\((.+)\)'))
async def size_button(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'size\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    user_id = update.from_user.id
    chat_id = update.message.chat.id

    member = await bot.get_chat_member(group_id, user_id)
    if not member.status in ('administrator','creator'):
        return await update.answer('Nice Try Kid xD', show_alert=True)

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(size|off|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Enable',  callback_data=f'fix(size|on|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Select Wether File Size Should Be Shown With Seperate Button ...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'capt\((.+)\)'), group=4)
async def custom_cap(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'capt\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)
    buttons = []

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(caption|off|{group_id})'), InlineKeyboardButton('Change', callback_data=f'fix(caption|set|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Add New',  callback_data=f'fix(caption|set|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Change Or Add A Custom Caption...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'fsub\((.+)\)'), group=4)
async def fsub(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'fsub\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)
    buttons = []

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(fsub|off|{group_id})'), InlineKeyboardButton('Change', callback_data=f'fix(fsub|set|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Add New',  callback_data=f'fix(fsub|set|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Change Or Add A Fsub Channel...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'global\((.+)\)'))
async def global_filters(bot:Client, update:Message):

    status, group_id = re.findall(r'global\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    user_id = update.from_user.id
    chat_id = update.message.chat.id

    member = await bot.get_chat_member(group_id, user_id)
    if not member.status in ('administrator','creator'):
        return await update.answer('Nice Try Kid xD', show_alert=True)

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(global|off|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Enable',  callback_data=f'fix(global|on|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Toggle Global Filter On/Off ...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'spell\((.+)\)'), group=4)
async def spell_check(bot:Client, update:CallbackQuery):

    status, group_id = re.findall(r'spell\((.+)\)', update.data)[0].split('|',1)
    group_id = int(group_id)
    member = await bot.get_chat_member(group_id, update.from_user.id)
    if not member.status in ("administrator", "creator"):
        return await update.answer("Nice Try Kid xD", show_alert=True)
    buttons = []

    if status=='on':
        buttons = [[InlineKeyboardButton('❌ Disable ❌', callback_data=f'fix(noresult|off|{group_id})'), InlineKeyboardButton('Change', callback_data=f'fix(noresult|set|{group_id})'), InlineKeyboardButton('Default', callback_data=f'fix(noresult|def|{group_id})')]]
    elif status=='off':
        buttons = [[InlineKeyboardButton('Default', callback_data=f'fix(noresult|def|{group_id})'), InlineKeyboardButton('Add New',  callback_data=f'fix(noresult|set|{group_id})')]]
    buttons.append([
            InlineKeyboardButton
                (
                    "🔙 Back", callback_data="settings"
                ),
            
            InlineKeyboardButton
                (
                    "Close 🔐", callback_data="close"
                )
        ])

    await update.message.edit_text("Use The Buttons Below To Change Or Add A Spell Check Message...", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r'gen_link\((.+)\)'), group=4)
async def privat_link_gen(bot:Client, update:CallbackQuery):

    try:

        group_id = re.findall(r'gen_link\((.+)\)', update.data)[0]
        group_id = int(group_id)
        member = await bot.get_chat_member(group_id, update.from_user.id)
        if not member.status in ("administrator", "creator"):
            return await update.answer("Nice Try Kid xD", show_alert=True)

        try :
            count = await bot.get_chat_members_count(group_id)
        except :
            count = 0
        if count < 50:
            return await update.answer(f"You Have To Adminsitrate A Group With Atleast 50 Memebers To Use This Feature :(", show_alert=True)
        else:
            link = await bot.create_chat_invite_link(-1001547869793)
            try:
                await bot.send_message(update.from_user.id, f"Use This Link To Join The Channel : {link.invite_link}\n\nIt Will Be Revoked Soon So Hurry")
                await update.answer("I've PM The Link To Channel In PM :)")
            except :
                return await update.answer("Please Start Or Unblock Me First :(")

    except Exception as e:

        await update.answer(str(e), show_alert=True)