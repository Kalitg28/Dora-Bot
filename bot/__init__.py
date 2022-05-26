#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) @AlbertEinsteinTG

import os
import logging
import time
from flask import Flask

from logging.handlers import RotatingFileHandler

from .translation import Translation
from .buttons import Buttons
from .helpers import Helpers

# Change Accordingly While Deploying To A VPS
APP_ID = int(os.environ.get("APP_ID",123))

API_HASH = os.environ.get("API_HASH",'okda')

BOT_TOKEN = os.environ.get("BOT_TOKEN",'innapidicho')

DB_URI = os.environ.get("DB_URI",'enichumvenam')

USER_SESSION = os.environ.get("USER_SESSION",'lo')

VERIFY = {}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "autofilterbot.txt",
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

start_uptime = time.time()


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
