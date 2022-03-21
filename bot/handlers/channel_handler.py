from pyrogram import Client, filters
from pyrogram.types import Message

from bot.plugins.channel import new_files, new_in_channel



@Client.on_message(filters.chat([-1001774321778, -1001547869793, -1001647894448]) & (filters.video | filters.document) & ~filters.edited, group=5)
async def new_files_manager(bot, update):

    await new_files(bot, update)

@Client.on_chat_member_updated(filters.chat(-1001547869793), group=5)
async def new_channel_member_handler(bot, update):

    await new_in_channel(bot, update)