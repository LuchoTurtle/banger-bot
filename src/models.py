import enum
from dataclasses import dataclass


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

