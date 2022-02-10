import re
import magic
import youtube_dl

from src.definitions.definitions import FILES_DIR
from src.exceptions import YoutubeAudioDownloadFail
from src.models import YoutubeTrack


def url_is_youtube_valid(url: str):
    """
    Validates if it is a proper youtube video and not a channel link or something.
    @param url: string to be verified.
    @return: returns if it's a valid youtube video link downloadable by Youtube DL.
    """
    pattern = re.compile(
        r"(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]+)")
    return pattern.search(url)


def download_youtube_audio(url: str) -> YoutubeTrack:
    """
    Downloads audio from youtube video link.
    @param url: youtube URL
    @return: YoutubeTrack containing information about the downloaded file and audio track.
    """

    # YoutubeDL options (best quality possible mp3 and outputting to files directory "files/ID.mp3")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': FILES_DIR + '%(id)s.%(ext)s'
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Download and get file info
            info = ydl.extract_info(url, download=True)

            title = info['title']
            video_id = info['id']

            filepath = FILES_DIR + video_id + '.mp3'
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(filepath)

    except Exception:
        raise YoutubeAudioDownloadFail

    return YoutubeTrack(title=title, video_id=video_id, filepath=filepath, mimetype=mimetype)