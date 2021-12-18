import logging
import re
import asyncio

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

from src.models import File, Action
from src.services.gdrive import get_creds, upload_to_drive
from src.services.youtube import youtube_callback

from src.services.shazam import shazam

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


def audio_file_handler(update: Update, context: CallbackContext) -> None:
    """
    Function that is called whenever an audio file is sent to the chat. It creates an inline keyboard with two possible options.
    @param update: Update object of message.
    @param context: Callback Context object.
    @return:
    """
    shazam_obj: File = File(Action.SHAZAM,
                            update.message.audio.title,
                            update.message.audio.file_id,
                            update.message.audio.mime_type,
                            update.effective_chat.id)

    direct_obj: File = File(Action.GDRIVE_UPLOAD,
                            update.message.audio.title,
                            update.message.audio.file_id,
                            update.message.audio.mime_type,
                            update.effective_chat.id)

    keyboard = [
        [
            InlineKeyboardButton("Shazam ⚡",
                                 callback_data=shazam_obj),
            InlineKeyboardButton("Drive Upload ⬆",
                                 callback_data=direct_obj),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('What do you want to do with this audio file?', reply_markup=reply_markup)


def audio_file_handler_button(update: Update, context: CallbackContext):
    """
    Audio file inline button callback function. This function processes the action chosen.
    @param update: Update object of message.
    @param context: Callback Context object.
    @return:
    """

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    query.answer()

    answer_file: File = query.data

    # Download file locally
    file = context.bot.getFile(answer_file.file_id)
    file.download(answer_file.get_file_location())

    # Check if the user wants to Shazam or directly upload the file to the Google Drive account
    if answer_file.action is Action.SHAZAM:
        query.edit_message_text("Please wait while we detect the song ⌛")

        song_title = asyncio.run(
            shazam(answer_file, context)
        )

        query.edit_message_text(text=f"We found a song! Here's the title: {song_title}")

    elif answer_file.action is Action.GDRIVE_UPLOAD:
        query.edit_message_text("Please wait while we upload the song ⌛")

        upload_to_drive(answer_file.get_file_location(), answer_file.file_title, answer_file.mime_type)

        query.edit_message_text(text=f"Song uploaded!")

    else:
        query.edit_message_text("That action is not permitted 🙁")


def main():
    """Start the bot."""
    get_creds()

    # Create the Updater and get dispatcher to register handlers
    updater = Updater(config("BOT_TOKEN"), use_context=True, arbitrary_callback_data=True)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.audio, audio_file_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(audio_file_handler_button))

    dispatcher.add_handler(MessageHandler(Filters.entity("url"), url_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
