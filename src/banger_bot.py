import logging
import re

from decouple import config
from linkpreview import link_preview
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from gdrive import get_creds, file_handler


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger("BangerBot")

## Definir google drive token -> fazer upload para lá. O Bot pega nos links e faz o upload tudo automaticamente. Depois até podemos dizer quanto espaço falta ou não

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text(
"""Hi! Welcome Banger Bot! 👋\n
The bot is still under development but it is mainly intended for you and your friends to share music on a group chat and automatically upload it to a Google Drive folder you set up. \n
Enjoy your music with your friends!🎉 """
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""

    # TODO Organize code, get more detailed metadata from URLs
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = (re.findall(regex, update.message.text)[0])[0]

    preview = link_preview(url)

    message = (
            update.message.from_user.full_name
            + " provided a link from "
            + preview.link.netloc
            + "\nWe getting there boys"
    )

    update.message.reply_text(message)
    logger.log(level=logging.INFO, msg=message)


def main():
    get_creds()
    """Start the bot."""

    # TODO verify chat ID only for us
    # Create the Updater
    updater = Updater(config("BOT_TOKEN"), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.audio, file_handler))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand with message in url
    # TODO create filter for known providers : Spotify, Apple Music, SoundCloud, etc
    dispatcher.add_handler(MessageHandler(Filters.entity("url"), echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
