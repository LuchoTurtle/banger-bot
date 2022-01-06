import os

from telegram.ext import CallbackContext
from shazamio import Shazam

from exceptions import TrackNotFound
from models import File, ShazamTrack


# TODO We need to find a way to automatically instapp ffmpeg and add it to path variable before running, it's needed
#  for Shazam
async def shazam(file: File, context: CallbackContext) -> ShazamTrack:
    file_location = file.get_file_location()

    file_obj = context.bot.getFile(file.file_id)
    file_obj.download(file_location)

    shazam_obj = Shazam()
    unserialized_track = await shazam_obj.recognize_song(file_location)

    try:
        os.remove(file_location)
    except Exception as e:
        raise Exception("Problem removing file after Shazam.")

    try:
        serialized_track = ShazamTrack(unserialized_track)
    except TrackNotFound:
        raise TrackNotFound

    return serialized_track
