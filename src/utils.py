from mutagen.easyid3 import EasyID3


def set_file_metadata(filepath: str, title: str, artist: str = None, track_num: int = None):
    """
    Set file's artist, track number and title metadata.
    @param filepath: path to the file.
    @param title: song title.
    @param artist: artist name.
    @param track_num: track number.
    @return:
    """
    metatag = EasyID3(filepath)

    metatag['title'] = title
    if artist: metatag['artist'] = artist
    if track_num: metatag['track'] = track_num

    metatag.save()
