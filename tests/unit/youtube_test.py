from unittest.mock import Mock, AsyncMock

import pytest
import os 

from src.models import Metadata
from src.exceptions import YoutubeAudioDownloadFail
from src.services.youtube import url_is_youtube_valid, download_youtube_audio
import yt_dlp


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
@pytest.mark.asyncio
async def test_download_audio_normal(mocker):
    """Normal callback behaviour"""

    message_mock = Mock()

    metadata: Metadata = Metadata("https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO", "", "", "", "", "", "", "")

    youtube_track = await download_youtube_audio(metadata, message_mock)

    # Asserts
    assert youtube_track.file_title == "Porter Robinson - Goodbye To A World (Official Audio)"
    
    # Remove downloaded file
    os.remove(youtube_track.filepath)


# @pytest.mark.asyncio
# async def test_error_downloading_audio(mocker):
#     """Errors because there was a problem downloading Youtube file"""
# 
#     message_mock = Mock()
#     
#     # Youtube
#     ydl_mock = Mock()
#     ydl_mock.extract_info.return_value = {
#         "title": "sample",
#         "id": "sample"
#     }
# 
#     mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.side_effect = Exception
#     metadata: Metadata = Metadata("https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO", "", "", "", "", "", "", "")
# 
#     with pytest.raises(YoutubeAudioDownloadFail):
#         await download_youtube_audio(metadata, message_mock)