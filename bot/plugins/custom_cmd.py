
from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, PeerIdInvalid, ChannelInvalid
from pyrogram.types.messages_and_media.message import Message
from bot.database import Database # pylint: disable=import-error

db = Database()



async def toggle_gf(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        return

    extract = update.text.split()
    if len(extract)<2:
        await update.reply("You Havent Specified An Operand On/Off :(")
        return

    operand = extract[1].lower()
    if operand=='on':
        await db.set_main(chat_id, 'global', True)
        await update.reply_text("GlobalFilter Is Now Enabled :)")
    elif operand=='off':
        await db.del_main(chat_id, 'global')
        await update.reply_text("GlobalFilter Was Disabled :(")
    else:
        await update.reply_text(f"Invalid Operand {operand} Only On/Off Can Be Used")

async def toggle_af(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        return

    extract = update.text.split()
    if len(extract)<2:
        await update.reply("You Havent Specified An Operand On/Off :(")
        return

    operand = extract[1].lower()
    if operand=='on':
        await db.set_main(chat_id, 'af', True)
        await update.reply_text("AutoFilter Is Now Enabled :)")
    elif operand=='off':
        await db.del_main(chat_id, 'af')
        await update.reply_text("AutoFilter Was Disabled :(")
    else:
        await update.reply_text(f"Invalid Operand {operand} Only On/Off Can Be Used")

async def toggle_autodel(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        return

    extract = update.text.split()
    if len(extract)<2:
        await update.reply("You Havent Specified An Operand On/Off :(")
        return

    operand = extract[1].lower()
    if operand=='on':
        if len(extract)<3:
            await db.set_main(chat_id, 'autodel', 15*60)
            await update.reply("AutoDelete Timer Was Set To The Default 15 mins")
            return
        else:
            try:
                value = int(extract[2])*60
                await db.set_main(chat_id, 'autodel', value)
                return await update.reply_text(f"AutoDelete Timer Was Successfully Set To {extract[2]} Minutes :)")
            except TypeError:
                await db.set_main(chat_id, 'autodel', 15*60)
                await update.reply_text(f"{extract[2]} isnta A Valid Value :( So Default Value Of 15 Minutes Was Set")
    elif operand=='off':
        await db.del_main(chat_id, 'autodel')
        await update.reply_text("The AutoDelete Timer Was Disabled :)")
    else:
        await update.reply_text(f"Invalid Operand {operand} Only On/Off Can Be Used")


async def delfsub(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        return

    await db.del_main(chat_id, 'fsub')
    await update.reply_text("Existing Fsub Channel Was Remmoved Successfully :)")

async def setfsub(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        return
    
    extract = update.text.split()
    if len(extract)<2:
        await update.reply("You Havent Specified A ChatID Bro Add me there and send /id to get the channel's id :)")
        return
        
    try :
        fsub_chat = int(extract[1])

        chat = await bot.get_chat(fsub_chat)
        title = chat.title
        id = chat.id
        result = dict(
                    id=id,
                    title=title
                )

        await db.set_main(chat_id, 'fsub', result)
    except TypeError:
        return await update.reply_text("That Doesnt Look Like A Valid ChatID...")
    except PeerIdInvalid:
        return await update.reply_text("Oh no looks Like I'm Not A Member Of This Channel Please Add Me There First...")
    except ChannelInvalid:
        return await update.reply_text("Oh no looks Like I'm Not A Member Of This Channel Please Add Me There First...")

async def setcaption(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        print(e)
        return
    
    extract = update.text.split(None, 1)
    if len(extract)<2:
        await update.reply("You Havent Specified A Caption Bro")
        return
    caption = extract[1]

    await db.set_main(int(chat_id), "caption", caption)
    await update.reply("Your Custom Caption Was Saved Successfully...", quote=True)

async def delcaption(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return

    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        print(e)
        return

    await db.del_main(int(chat_id), "caption")
    await update.reply("Your Request Was Updated Successfully", quote=True)

async def setspell(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return
        
    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        await update.reply_text(f"Something Went Wrong : {e} \nPlease Contact My Support Team :(")
        print(e)
        return
    
    extract = update.text.split(None, 1)
    if len(extract)<2:
        await update.reply("You Havent Specified A Message Bro")
        return
    caption = extract[1]

    await db.set_main(int(chat_id), "noresult", caption)
    await update.reply("Your Custom Spelling Message Was Saved Successfully...", quote=True)

async def delspell(bot:Client, update:Message):

    chat_id = update.chat.id
    chat_type = update.chat.type

    if chat_type=="private":

        chat_id = await db.get_conn(chat_id)
        if not chat_id:

            await update.reply("Connect To A Chat First To Use This Command From PM")
            return

    try:
        if update.from_user.id:
            member = await bot.get_chat_member(int(chat_id), update.from_user.id)
            if member.status not in ("administrator", "creator"):
                await update.reply("Thats Not For You ...")
                return
    except UserNotParticipant:
        await update.reply("Your Not even In This Chat")
        return
    except Exception as e:
        print(e)
        return

    await db.del_main(int(chat_id), "noresult")
    await update.reply("Your Request Was Updated Successfully", quote=True)

#async def toggle_af(bot:Client, update:Message):
#    '''
#    A Function to toggle AutoFilter Mode
#    '''
#    user_id = update.from_user.id
#    chat_id = update.chat.id
#    chat_type = update.chat.type
#
#    if chat_type=="private":
#
#        chat_id = await db.get_conn(chat_id)
#
#    if not chat_id:
#
#        await update.reply_text("Please Connect To A Chat First To Use This Bot In PM", quote=True)
#        return
#
#    member = await bot.get_chat_member(chat_id, user_id)
#    if not member.status in ('administrator','creator'):
#        return #Return if User Isnt Admin
#
#    prev = await db.find_chat(chat_id)
#
#    accuracy = float(prev["configs"].get("accuracy", 0.70))
#    max_pages = int(prev["configs"].get("max_pages"))
#    max_results = int(prev["configs"].get("max_results"))
#    max_per_page = int(prev["configs"].get("max_per_page"))
#    pm_file_chat = True if prev["configs"].get("pm_fchat") == (True or "True") else False
#    show_invite_link = True if prev["configs"].get("show_invite_link") == (True or "True") else False
#
#    action = update.text.lower().split(' ',1)[1]
#    if action=='on':
#        af=True
#    elif action=='off':
#        af = False
#    else:
#        return await update.reply("Invalid Action Action Can Only Be On/Off")
#
#    new = dict(
#        accuracy=accuracy,
#        max_pages=max_pages,
#        max_results=max_results,
#        max_per_page=max_per_page,
#        pm_fchat=pm_file_chat,
#        show_invite_link=show_invite_link,
#        af=af
#    )
#    
#    append_db = await db.update_configs(chat_id, new)
#    
#    if not append_db:
#        await update.reply_text("Something Wrong Please Check Bot Log For More Information....")
#        return
#    else:
#        await update.reply_text("Your Request Was Updated Successfully...")
#        return

