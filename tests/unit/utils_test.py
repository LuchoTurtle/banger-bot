from src.utils import get_metadata_from_message


def test_get_metadata_from_message():
    """Test different scenarios on extracting metadata from message."""

    message = "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    ret = get_metadata_from_message(message)
    assert ret.url is not "" and ret.url == "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    assert ret.artist is "" and ret.title is "" and ret.album is "" and ret.folder is None and ret.year is ""

    message = "https://www.youtube.com/watch?v=lSooYPG-5Rg && folder:  some folder name && artist: potaro"
    ret = get_metadata_from_message(message)
    assert ret.url is not "" and ret.url == "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    assert ret.artist == 'potaro'
    assert ret.folder == 'some folder name'

    message = "folder:  some folder name && artist: potaro"
    ret = get_metadata_from_message(message)
    assert ret.url is ""
    assert ret.artist == 'potaro'
    assert ret.folder is None

    message = "https://www.youtube.com/watch?v=lSooYPG-5Rg && track: 123 && year: 2014"
    ret = get_metadata_from_message(message)
    assert ret.url is not "" and ret.url == "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    assert ret.track == 123
    assert ret.year == 2014

    message = "https://www.youtube.com/watch?v=lSooYPG-5Rg && track: invalid_track"
    ret = get_metadata_from_message(message)
    assert ret.url is not "" and ret.url == "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    assert ret.track is ""

    message = "https://www.youtube.com/watch?v=lSooYPG-5Rg & track: 1"
    ret = get_metadata_from_message(message)
    assert ret.url is not "" and ret.url == "https://www.youtube.com/watch?v=lSooYPG-5Rg"
    assert ret.track is ""
