import logging
import re

import requests
import youtube_dl
import magic

from decouple import config
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

from gdrive import get_creds, file_handler, upload_to_drive

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("BangerBot")


## Definir google drive token -> fazer upload para lá. O Bot pega nos links e faz o upload tudo automaticamente. Depois até podemos dizer quanto espaço falta ou não

def start(update: Update, context: CallbackContext) -> None:
    logger.log(level=logging.INFO, msg="Bot initiated with /start command.")
    update.message.reply_text(
        """*Hi! Welcome Banger Bot!* 👋\n
The bot is still under development but it is mainly intended for you and your friends to share music on a group chat and automatically upload it to a Google Drive folder you set up. \n
Enjoy your music with your friends! 🎉 
    """, parse_mode=ParseMode.MARKDOWN)


def help_command(update: Update, context: CallbackContext) -> None:
    logger.log(level=logging.INFO, msg="Printed /help command.")
    update.message.reply_text("""
*We're here to help!* 😀\n
For the bot to properly work, you need a _Google Drive project set up and authorize this bot on startup to edit it_. 
From there on, the bot will listen to relevant URLs and take care of downloading and uploading your music to Google Drive. \n
Do you want some guidance setting everything up step-by-step? Click the button below to check our Github repository 
and find all the info needed there! 😊
""", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Github Page', url='https://github.com/LuchoTurtle/banger-bot')],
    ]),
                              parse_mode=ParseMode.MARKDOWN)


def url_is_valid(update: Update, context: CallbackContext, url: str) -> bool:
    youtube_pattern = re.compile(
        "(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]+)")
    if not bool(youtube_pattern.search(url)):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="This URL does not point to a valid Youtube video ❌.\nAre you sure it's not a channel? 🤔",
                                 parse_mode=ParseMode.MARKDOWN)
        return False
    return True


def youtube_callback(update: Update, context: CallbackContext, url: str) -> None:
    if url_is_valid(update, context, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '../files/%(title)s.%(ext)s'
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Got it! ✅\nGoing to download the file now and try to upload it to Google Drive. Gimme a few seconds!",
                                         parse_mode=ParseMode.MARKDOWN)

                # Download and get file info
                info = ydl.extract_info(url, download=True)

                filepath = ydl.prepare_filename(info)
                title = info['title']
                mime = magic.Magic(mime=True)
                mimetype = mime.from_file(filepath)

                try:
                    # Upload to GDrive
                    upload_to_drive(filepath, title, mimetype)

                    # Send confirmation message
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Your song *" + title + "* has been uploaded ✅",
                                             parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    logger.log(level=logging.ERROR, msg="Error uploading file to Google Drive.\n")
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="There was an error uploading this file to Google Drive ❌.\nHave you set up everything correctly? 🤔",
                                             parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.log(level=logging.ERROR, msg="Error downloading youtube file.\n")
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="There was an error downloading this Youtube video ❌.\nHave you checked if it's available? 🤔",
                                     parse_mode=ParseMode.MARKDOWN)


def url_handler(update: Update, context: CallbackContext) -> None:
    # TODO Organize code, get more detailed metadata from URLs
    # TODO create filter for known providers : Spotify, Apple Music, SoundCloud, etc
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = (re.findall(url_regex, update.message.text)[0])[0]

    youtube_pattern = re.compile(
        "(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/?)")
    if bool(youtube_pattern.search(url)):
        youtube_callback(update, context, url)
    else:
        update.message.reply_text("We are yet to support URLs from this place. 😕", parse_mode=ParseMode.MARKDOWN)


def main():
    """Start the bot."""
    get_creds()

    # TODO verify chat ID only for us

    # Create the Updater and get dispatcher to register handlers
    updater = Updater(config("BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.audio, file_handler))
    dispatcher.add_handler(MessageHandler(Filters.entity("url"), url_handler))

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
