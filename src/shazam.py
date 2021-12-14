import os

from telegram.ext import CallbackContext
from shazamio import Shazam
from definitions import ROOT_DIR


# TODO We need to find a way to automatically instapp ffmpeg and add it to path variable before running, it's needed
#  for Shazam
async def shazam(title: str, file_id, context: CallbackContext):
    file_location = '../files/' + title

    file = context.bot.getFile(file_id)
    file.download(file_location)

    shazam_obj = Shazam()
    track = await shazam_obj.recognize_song(file_location)

    try:
        os.remove(ROOT_DIR + '/files/' + title)
    except Exception as e:
        raise Exception("Problem removing file after Shazam.")

    finally:
        return track.get('track').get('title')
