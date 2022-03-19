#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @SpEcHIDe

import pyromod.listen

from pyrogram import Client, __version__

from . import API_HASH, APP_ID, LOGGER, BOT_TOKEN 

from .user import User

class Bot(Client):
    USER: User = None
    USER_ID: int = None

    def __init__(self):
        super().__init__(
            "bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "bot/handlers"
            },
            workers=200,
            bot_token=BOT_TOKEN,
            sleep_threshold=10
        )
        self.LOGGER = LOGGER

    def start(self):
        super().start()
        bot_details = self.get_me()
        self.set_parse_mode("html")
        self.LOGGER(__name__).info(
            f"@{bot_details.username}  started! "
        )
        self.USER, self.USER_ID = User().start()

    def stop(self, *args):
        super().stop()
        self.LOGGER(__name__).info("Bot stopped. Bye.")
