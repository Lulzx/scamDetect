#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import logging
import pytesseract

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hello! I am a bot to detect crypto scam tweets from screenshots.')


def help(update, context):
    update.message.reply_text('Simply send to me an image or add me to a group.')


def echo(update, context):
    chat_id = update.message.chat.id
    file_id = update.message.photo[0].file_id
    file_name = file_id + ".png"

    context.bot.get_file(file_id).download('./data/{}'.format(file_name))
    text = pytesseract.image_to_string('./data/{}'.format(file_name))

    if len(text) < 4:
        return

    choices = ["sent to my address", "giveaway", "bitcoin", "ethereum", "crypto"]
    ratio = process.extractOne(text, choices, scorer=fuzz.partial_ratio)

    if ratio[1] > 30:
        text = "spam detected"
        context.bot.send_message(chat_id=chat_id, text=text)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    try:
        TOKEN = sys.argv[1]
    except IndexError:
        TOKEN = os.environ.get("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.photo, echo))
    dp.add_error_handler(error)
    updater.start_polling(clean=True, timeout=99999)
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
