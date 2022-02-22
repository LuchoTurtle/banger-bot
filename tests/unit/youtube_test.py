from unittest.mock import Mock

import pytest

from src.exceptions import YoutubeAudioDownloadFail
from src.services.youtube import url_is_youtube_valid, download_youtube_audio


# URL is valid -----------------
def test_url_is_valid():
    """URL passed is valid or invalid"""

    # Valid
    ret = url_is_youtube_valid("https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15")
    assert ret

    # Invalid
    ret_c = url_is_youtube_valid("https://www.youtube.com/c/porterrobinson")
    assert not ret_c

    ret_g = url_is_youtube_valid("https://www.google.com")
    assert not ret_g


# Download youtube_audio --------------------
def test_download_audio_normal(mocker):
    """Normal callback behaviour"""

    message_mock = Mock()

    # Youtube
    ydl_mock = Mock()
    ydl_mock.extract_info.return_value = {
        "title": "sample",
        "channel": "Porter Robinson",
        "id": "sample"
    }

    # Mock and execute the function
    mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.return_value = ydl_mock

    youtube_track = download_youtube_audio("https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15", message_mock)

    # Asserts
    ydl_mock.extract_info.assert_called_once()
    assert youtube_track.title == "sample"
    assert youtube_track.video_id == "sample"


def test_error_downloading_audio(mocker):
    """Errors because there was a problem downloading Youtube file"""

    message_mock = Mock()

    # Youtube
    ydl_mock = Mock()
    ydl_mock.extract_info.return_value = {
        "title": "sample",
        "id": "sample"
    }

    mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.side_effect = Exception

    with pytest.raises(YoutubeAudioDownloadFail):
        download_youtube_audio("https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15", message_mock)