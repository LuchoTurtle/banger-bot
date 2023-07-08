import re
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes
)

from src.exceptions import YoutubeAudioDownloadFail, GoogleDriveUploadFail
from src.services.gdrive import upload_to_drive
from src.services.youtube import url_is_youtube_valid, download_youtube_audio

from src.models import File, Action, ShazamTrack, Metadata
from src.services.shazam import shazam
from src.exceptions import TrackNotFound
from src.utils import get_metadata_from_message


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        """*Hi! Welcome Banger Bot!* 👋\n
The bot is still under development but it is mainly intended for you and your friends to share music on a group chat and automatically upload it to a Google Drive folder you set up. \n
Detect songs from Youtube and upload them. You can also Shazam it!
Enjoy your music with your friends! 🎉 
    """, parse_mode=ParseMode.MARKDOWN)

#TODO adding help to regex, shazam
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""
*We're here to help!* 😀\n
For the bot to properly work, you need a _Google Drive project set up and authorize this bot on startup to edit it_. 
From there on, the bot will listen to relevant URLs and take care of downloading and uploading your music to Google Drive. \n
Do you want some guidance setting everything up step-by-step? Click the button below to check our Github repository 
and find all the info needed there! 😊
""", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Github Page', url='https://github.com/LuchoTurtle/banger-bot')],
    ]),
                              parse_mode=ParseMode.MARKDOWN)


async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles what to do when an URL is detected on the message. It handles Youtube links, so far.
    @param update: Update object
    @param context: Context object
    @return: nothing.
    """
    # TODO Organize code, get more detailed metadata from URLs
    # TODO create filter for known providers : Spotify, Apple Music, SoundCloud, etc

    # Provider patterns
    youtube_pattern = re.compile("(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/?)")

    # Regex for the tag and url ( text <tag> <url>)
    message_metadata: Metadata = get_metadata_from_message(update.message.text)

    if message_metadata.url:

        # Youtube ------
        if bool(youtube_pattern.search(message_metadata.url)):

            # Check if it is a video that can be downloaded
            if not url_is_youtube_valid(message_metadata.url):
                await update.message.reply_text("This URL does not point to a valid Youtube video ❌.",
                                          parse_mode=ParseMode.MARKDOWN)
                return

            # Begin download
            msg = await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Got it! Going to download the file now and try to upload it to Google Drive. Gimme a few seconds ⌛!",
                                           parse_mode=ParseMode.MARKDOWN)

            try:
                track = download_youtube_audio(message_metadata, msg)
            except YoutubeAudioDownloadFail:
                msg.edit_text("There was a problem downloading the audio from this Youtube link ❌.",
                              parse_mode=ParseMode.MARKDOWN)
                return

            # Upload to Google Drive
            try:
                upload_to_drive(track.filepath, track.file_title, track.mimetype, msg, message_metadata.folder)
            except GoogleDriveUploadFail:
                msg.edit_text("We managed to download the audio but failed to upload on Google Drive ❌.",
                              parse_mode=ParseMode.MARKDOWN)
                return

            await update.message.reply_text("Your song *" + track.file_title + "* has been uploaded ✅.",
                                      parse_mode=ParseMode.MARKDOWN)

        # Other providers ------
        else:
            await update.message.reply_text("We are yet to support URLs from this place 😕.", parse_mode=ParseMode.MARKDOWN)


# Inline query handlers ------------------
async def audio_file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text('What do you want to do with this audio file?', reply_markup=reply_markup)


async def audio_file_handler_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Audio file inline button callback function. This function processes the action chosen.
    @param update: Update object of message.
    @param context: Callback Context object.
    @return:
    """

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    await query.answer()

    answer_file: File = query.data

    # Download file locally
    file = await context.bot.getFile(answer_file.file_id)
    await file.download_to_drive(answer_file.get_file_location())

    # Check if the user wants to Shazam or directly upload the file to the Google Drive account
    if answer_file.action is Action.SHAZAM:
        await query.edit_message_text("Please wait while we detect the song ⌛")

        try:
            track: ShazamTrack = await shazam(answer_file, context)

            await query.edit_message_text("We found a track! 🎉")

            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=track.image,
                                   caption=f'It\'s *{track.subtitle} - {track.title}*\n',
                                   parse_mode=ParseMode.MARKDOWN)

        except TrackNotFound:
            await query.edit_message_text(f'Unfortunately we couldn\'t detect a song ☹')

    elif answer_file.action is Action.GDRIVE_UPLOAD:
        await query.edit_message_text("Please wait while we upload the song ⌛")

        upload_to_drive(answer_file.get_file_location(), answer_file.file_title, answer_file.mime_type)

        await query.edit_message_text(text=f"Song uploaded!")

    else:
        await query.edit_message_text("That action is not permitted 🙁")