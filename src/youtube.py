import logging
import re

import magic
import youtube_dl
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.gdrive import upload_to_drive

logger = logging.getLogger("BangerBot")

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