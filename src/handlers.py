import re
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext
)

from src.exceptions import YoutubeAudioDownloadFail, GoogleDriveUploadFail
from src.services.gdrive import upload_to_drive
from src.services.youtube import url_is_youtube_valid, download_youtube_audio


def start_handler(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """*Hi! Welcome Banger Bot!* 👋\n
The bot is still under development but it is mainly intended for you and your friends to share music on a group chat and automatically upload it to a Google Drive folder you set up. \n
Detect songs from Youtube and upload them. You can also Shazam it!
Enjoy your music with your friends! 🎉 
    """, parse_mode=ParseMode.MARKDOWN)


def help_handler(update: Update, context: CallbackContext) -> None:
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

    # Provider patterns
    youtube_pattern = re.compile("(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/?)")

    # Regex for the tag and url ( text <tag> <url>)
    tag_regex = r".*\|"
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    # Checking if we match a tag and url
    url_match = re.search(url_regex, update.message.text)
    tag_match = re.search(tag_regex, update.message.text)

    if url_match:

        # Get tag and url
        tag = None
        if tag_match:
            tag = tag_match.group(0).replace("|", "").strip()

        url = url_match.group(0)

        # Youtube ------
        if bool(youtube_pattern.search(url)):

            # Check if it is a video that can be downloaded
            if not url_is_youtube_valid(url):
                update.message.reply_text("This URL does not point to a valid Youtube video ❌.", parse_mode=ParseMode.MARKDOWN)
                return

            # Begin download
            msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Got it!\nGoing to download the file now and try to upload it to Google Drive. Gimme a few seconds ⌛!",
                                     parse_mode=ParseMode.MARKDOWN)

            try:
                track = download_youtube_audio(url)
            except YoutubeAudioDownloadFail:
                msg.edit_text("There was a problem downloading the audio from this Youtube link ❌.", parse_mode=ParseMode.MARKDOWN)
                return

            # Upload to Google Drive
            try:
                upload_to_drive(track.filepath, track.title, track.mimetype, tag)
            except GoogleDriveUploadFail:
                msg.edit_text("We managed to download the audio but failed to upload on Google Drive ❌.", parse_mode=ParseMode.MARKDOWN)
                return

            update.message.reply_text("Your song *" + track.title + "* has been uploaded ✅.", parse_mode=ParseMode.MARKDOWN)

        # Other providers ------
        else:
            update.message.reply_text("We are yet to support URLs from this place 😕.", parse_mode=ParseMode.MARKDOWN)