import logging
import re
import asyncio
from shazamio import Shazam, serialize_track
import json

from decouple import config
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext
)
from src.gdrive import get_creds, file_handler
from src.youtube import youtube_callback

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("BangerBot")


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


# TODO We need to find a way to automatically instapp ffmpeg and add it to path variable before running, it's needed
#  for Shazam
async def shazam(title: str, file_id, context: CallbackContext):
    file_location = '../files/' + title

    file = context.bot.getFile(file_id)
    file.download(file_location)

    print(file_location)

    shazam_obj = Shazam()
    track = await shazam_obj.recognize_song(file_location)

    return track.get('track').get('title')


def audio_file_handler(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""

    shazam_obj = {
        "action": "shazam",
        "file_title": update.message.audio.title,
        "file_id": update.message.audio.file_id,
        "mime_type": update.message.audio.mime_type,
        "chat_id": update.effective_chat.id
    }

    direct_obj = {
        "action": "direct",
        "file_title": update.message.audio.title,
        "file_id": update.message.audio.file_id,
        "mime_type": update.message.audio.mime_type,
        "chat_id": update.effective_chat.id
    }

    keyboard = [
        [
            InlineKeyboardButton("Shazam",
                                 callback_data=shazam_obj),
            InlineKeyboardButton("Direct upload",
                                 callback_data=direct_obj),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose one of the following options:', reply_markup=reply_markup)


def audio_file_handler_button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    answer = query.data

    if answer.get('action') is 'shazam':
        song_title = asyncio.run(
            shazam(answer.get('file_title') + '.mp3', answer.get('file_id'), context)
        )

        query.edit_message_text(text=f"We found a song! Here's the title: {song_title}")
    else:
        file_handler(answer.get('file_title'), answer.get('file_id'), answer.get('mime_type'), answer.get('chat_id'), context)
        query.edit_message_text(text=f"Song uploaded!")


def main():
    """Start the bot."""
    get_creds()

    # TODO verify chat ID only for us

    # Create the Updater and get dispatcher to register handlers
    updater = Updater(config("BOT_TOKEN"), use_context=True, arbitrary_callback_data=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.audio, audio_file_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(audio_file_handler_button))

    dispatcher.add_handler(MessageHandler(Filters.entity("url"), url_handler))

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
