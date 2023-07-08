from decouple import config
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from src.handlers import start_handler, help_handler, url_handler, audio_file_handler, audio_file_handler_button
from src.services.gdrive import get_creds


def exec():
    """Start the bot."""
    get_creds()


    # Create the Updater and get application to register handlers
    application = Application.builder().token(config("BOT_TOKEN")).arbitrary_callback_data(True).build()
    updater = application.updater

    # Handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))

    application.add_handler(MessageHandler(filters.AUDIO, audio_file_handler))
    application.add_handler(MessageHandler(filters.VOICE, audio_file_handler))
    application.add_handler(CallbackQueryHandler(audio_file_handler_button))

    application.add_handler(MessageHandler(filters.Entity("url"), url_handler))

    application.run_polling()
    updater.idle()


if __name__ == "__main__":
    exec()
