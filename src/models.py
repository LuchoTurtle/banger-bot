import enum
from dataclasses import dataclass

from definitions import FILES_DIR


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


