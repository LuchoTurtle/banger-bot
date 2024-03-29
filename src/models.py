import enum
from dataclasses import dataclass

from src.definitions.definitions import FILES_DIR
from src.exceptions import TrackNotFound


class Action(enum.Enum):
    SHAZAM = "shazam"
    GDRIVE_UPLOAD = "gdrive"


@dataclass
class File:
    action: Action
    file_title: str
    file_id: str
    mime_type: str
    chat_id: str

    def get_file_location(self) -> str:
        """
        Get location of the file.
        @return: returns file location.
        """
        return FILES_DIR + self.file_title


@dataclass
class ShazamTrack:
    def __init__(self, music):
        try:
            self.track = music['track']
            self.title = self.track['title']
            self.image = self.track['images']['coverarthq']
            self.subtitle = self.track['subtitle']
            self.first_provider: dict = {
                "caption": self.track['hub']['providers'][0]['caption'],
                "uri": self.track['hub']['providers'][0]['actions'][0]['uri']
            }
        except KeyError:
            raise TrackNotFound


@dataclass
class YoutubeTrack:
    file_title: str
    video_id: str
    filepath: str
    mimetype: str


@dataclass
class Metadata:
    url: str
    artist: str
    year: int
    track: int
    genre: str
    album: str
    title: str
    folder: str
