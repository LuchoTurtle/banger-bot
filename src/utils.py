import re
from mutagen.easyid3 import EasyID3

from src.models import Metadata


def set_file_metadata(filepath: str, metadata: Metadata):
    """
    Set file's artist, track number and title metadata.
    @param filepath: file path to set metadata.
    @param metadata: metadata object.
    @return:
    """
    metatag = EasyID3(filepath)

    metatag['artist'] = metadata.artist
    metatag['date'] = metadata.year
    metatag['tracknumber'] = metadata.track
    metatag['genre'] = metadata.genre
    metatag['album'] = metadata.album
    metatag['title'] = metadata.title

    metatag.save()


def get_metadata_from_message(message: str) -> Metadata:
    """
    Parses message and extracts metadata.
    Message should have the format of <URL> && (artist:<artist> && folder:<folder>) -> '()' being optional.
    @param message: message to parse.
    @return: returns Metadata object with the extracted metadata
    """

    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    # Checking if there are any metadata matches
    url_match = re.search(url_regex, message)
    artist_match = re.search(r"(&&\s{0,}artist:([^&]{0,}))", message)
    year_match = re.search(r"(&&\s{0,}year:([^&]{0,}))", message)
    genre_match = re.search(r"(&&\s{0,}genre:([^&]{0,}))", message)
    album_match = re.search(r"(&&\s{0,}album:([^&]{0,}))", message)
    title_match = re.search(r"(&&\s{0,}title:([^&]{0,}))", message)
    folder_match = re.search(r"(&&\s{0,}folder:([^&]{0,}))", message)
    track_match = re.search(r"(&&\s{0,}track:([^&]{0,}))", message)

    # Retrieving values from matches
    url = url_match.group(0).strip() if url_match is not None else ""
    artist = artist_match.group(2).strip() if artist_match is not None else ""
    year = year_match.group(2).strip() if year_match is not None else ""
    genre = genre_match.group(2).strip() if genre_match is not None else ""
    album = album_match.group(2).strip() if album_match is not None else ""
    title = title_match.group(2).strip() if title_match is not None else ""
    folder = folder_match.group(2).strip() if folder_match is not None else None
    track = track_match.group(2).strip() if track_match is not None else ""

    # Parsing ints
    try:
        year = int(year)
    except: year = ""
    try:
        track = int(track)
    except: track = ""

    return Metadata(url=url,
                    artist=artist,
                    year=year,
                    genre=genre,
                    album=album,
                    title=title,
                    folder=folder,
                    track=track)
