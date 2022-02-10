from decouple import config
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)

from src.handlers import start_handler, help_handler, url_handler, audio_file_handler, audio_file_handler_button
from src.services.gdrive import get_creds


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
