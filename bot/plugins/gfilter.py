import pyrogram

from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from bot.database import Database # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.translation import Translation

db = Database()

@Bot.on_message(filters.text & filters.group & ~filters.bot, group=2)
async def global_filter(bot, update:Message):

    configs = await db.find_chat(update.chat.id)

    g_filter = configs.get('global', True)
    if not g_filter: return

    f_result = await db.find_mfilter(group_id=902, query=update.text)
    if not f_result :
        return
    else:
        content, file_id, btn, sticker = (f_result["content"], f_result["file_id"], f_result["buttons"], f_result["sticker"])
    if btn:
        print(btn)
        buttons = eval(btn)

    content:str = content.format(mention=update.from_user.mention, first_name=update.from_user.first_name, last_name=update.from_user.last_name, full_name=f"{update.from_user.first_name} {update.from_user.last_name}", username=update.from_user.username if update.from_user.username else update.from_user.first_name, id=update.from_user.id)

    if sticker and file_id:
        if buttons:
            await update.reply_sticker(
                sticker=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
                )
        else :
            await update.reply_sticker(sticker=file_id)
    elif file_id:
        if buttons:
            await update.reply_cached_media(
                file_id=file_id,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
                caption=content,
                quote=True
            )
        else:
            await update.reply_cached_media(
                file_id=file_id,
                parse_mode="html",
                caption=content,
                quote=True
            )
    else :
        if buttons:
            await update.reply_text(
                text=content,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
        else :
            await update.reply_text(
                text=content,
                parse_mode="html",
                quote=True
            )
async def all_gfilter(bot, update: Message):

    total_filters = ""

    filters = await db.all_mfilter(902)

    if not filters :
        await update.reply_text("Looks Like You Havent Saved Any Filters In Global", quote=True)
        return
    for filter in filters :
        total_filters+=f"\n- <code>{filter}</code>"

    await update.reply_text(f"Total Of {len(filters)} Manual Filters Have Been Saved For <b>Global</b> : {total_filters}", parse_mode="html", quote=True)
async def stopglobal(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id
    userid = update.from_user.id

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM", quote=True)
        return
    
    st = await bot.get_chat_member(chat_id, userid)

    print("Mark 2")
    if not ((st.status == "administrator") or (st.status == "creator") or (userid in (Translation.OWNER_ID,))):
        return

    splitted = update.text.split(None, 1)
    if len(splitted)<2:
        return await update.reply_text("Gimme A KeyWord Bro...")

    keyword = splitted[1] 

    globals = await db.all_mfilter(902)
    settings = await db.find_chat(chat_id)
    prev = settings.get('stopped',[])

    if keyword in prev:
        return await update.reply_text("You've Already Stopped This Filter In This Chat...")
    elif not keyword in globals:
        return await update.reply_text(f"Looks Like There Is No Global Filter For `{keyword}`")
    else :
        new = prev.append(keyword)
    
    await db.set_main(chat_id, 'stopped', new)
    await update.reply_text(f"The Global Filter for {keyword} will no longer work in this chat...")

async def startglobal(bot, update: Message):

    chat_type = update.chat.type
    chat_id = update.chat.id
    userid = update.from_user.id

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)

    if not chat_id:

        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM", quote=True)
        return
    
    st = await bot.get_chat_member(chat_id, userid)

    print("Mark 2")
    if not ((st.status == "administrator") or (st.status == "creator") or (userid in (Translation.OWNER_ID,))):
        return

    splitted = update.text.split(None, 1)
    if len(splitted)<2:
        return await update.reply_text("Gimme A KeyWord Bro...")

    keyword = splitted[1] 

    globals = await db.all_mfilter(902)
    settings = await db.find_chat(chat_id)
    prev = settings.get('stopped',[])

    if not keyword in prev:
        return await update.reply_text("You've Already Started This Filter In This Chat...")
    elif not keyword in globals:
        return await update.reply_text(f"Looks Like There Is No Global Filter For `{keyword}`")
    else :
        index = prev.index(keyword)
        new = prev.pop(index)
    
    await db.set_main(chat_id, 'stopped', new)
    await update.reply_text(f"The Global Filter for {keyword}  Will Work in this chat...")