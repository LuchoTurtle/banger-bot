import logging
import re
import youtube_dl

from decouple import config
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

from gdrive import get_creds, file_handler

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


def youtube_callback(url) -> None:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '../files/%(title)s.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # TODO upload to gdrive


def echo(update: Update, context: CallbackContext) -> None:
    # TODO Organize code, get more detailed metadata from URLs
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = (re.findall(regex, update.message.text)[0])[0]

    if 'youtube' in url:
        youtube_callback(url)

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
    # TODO create filter for known providers : Spotify, Apple Music, SoundCloud, etc
    dispatcher.add_handler(MessageHandler(Filters.entity("url"), echo))

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
