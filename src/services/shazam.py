import os

from telegram.ext import CallbackContext
from shazamio import Shazam

from src.exceptions import TrackNotFound, RemoveFileFailed
from src.models import File, ShazamTrack


# TODO We need to find a way to automatically install ffmpeg and add it to path variable before running, it's needed
#  for Shazam
async def shazam(file: File, context: CallbackContext) -> ShazamTrack:
    file_location = file.get_file_location()
    if not os.path.isfile(file_location):
        raise FileNotFoundError

    shazam_obj = Shazam()
    unserialized_track = await shazam_obj.recognize_song(file_location)

    try:
        os.remove(file_location)
    except Exception as e:
        raise RemoveFileFailed("Problem removing file after Shazam.")

    try:
        serialized_track = ShazamTrack(unserialized_track)
    except TrackNotFound:
        raise TrackNotFound

    return serialized_track
