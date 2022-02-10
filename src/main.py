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

from src.exceptions import TrackNotFound
from src.handlers import start_handler, help_handler, url_handler
from src.models import File, Action, ShazamTrack
from src.services.gdrive import get_creds, upload_to_drive
from src.services.shazam import shazam


def audio_file_handler(update: Update, context: CallbackContext) -> None:
    """
    Function that is called whenever an audio file is sent to the chat. It creates an inline keyboard with two possible options.
    @param update: Update object of message.
    @param context: Callback Context object.
    @return:
    """

    message_type = None
    if update.message.audio is not None:
        message_type = "audio"
    elif update.message.voice is not None:
        message_type = "voice"

    if message_type == "audio":
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

    elif message_type == "voice":
        shazam_obj: File = File(Action.SHAZAM,
                                update.message.voice.file_unique_id,
                                update.message.voice.file_id,
                                update.message.voice.mime_type,
                                update.effective_chat.id)

        direct_obj: File = File(Action.GDRIVE_UPLOAD,
                                update.message.voice.file_unique_id,
                                update.message.voice.file_id,
                                update.message.voice.mime_type,
                                update.effective_chat.id)

    else:
        return None

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

        try:
            track: ShazamTrack = asyncio.run(
                shazam(answer_file, context)
            )

            query.edit_message_text("We found a track! 🎉")

            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=track.image,
                                   caption=f'It\'s *{track.subtitle} - {track.title}*\n',
                                   parse_mode=ParseMode.MARKDOWN)

        except TrackNotFound:
            query.edit_message_text(f'Unfortunately we couldn\'t detect a song ☹')

    elif answer_file.action is Action.GDRIVE_UPLOAD:
        query.edit_message_text("Please wait while we upload the song ⌛")

        upload_to_drive(answer_file.get_file_location(), answer_file.file_title, answer_file.mime_type)

        query.edit_message_text(text=f"Song uploaded!")

    else:
        query.edit_message_text("That action is not permitted 🙁")


def exec():
    """Start the bot."""
    get_creds()

    # Create the Updater and get dispatcher to register handlers
    updater = Updater(config("BOT_TOKEN"), use_context=True, arbitrary_callback_data=True)
    dispatcher = updater.dispatcher

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CommandHandler("help", help_handler))

    dispatcher.add_handler(MessageHandler(Filters.audio, audio_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.voice, audio_file_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(audio_file_handler_button))

    dispatcher.add_handler(MessageHandler(Filters.entity("url"), url_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    exec()
