from unittest.mock import Mock

from src.exceptions import YoutubeAudioDownloadFail, GoogleDriveUploadFail
from src.models import YoutubeTrack
from src.main import start_handler, help_handler
import src.handlers
from src.handlers import url_handler


def test_start():
    """Test start command replies to message"""

    # Update mock
    message_mock = Mock()
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Callback mock
    callback_mock = Mock()

    start_handler(update_mock, callback_mock)

    assert update_mock.message.reply_text.called is True
    assert "Welcome" in update_mock.message.reply_text.call_args[0][0]


def test_help():
    """Test help command replies to message"""

    # Update mock
    message_mock = Mock()
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Callback mock
    callback_mock = Mock()

    help_handler(update_mock, callback_mock)

    assert update_mock.message.reply_text.called is True
    assert "help" in update_mock.message.reply_text.call_args[0][0]


# URL handler tests ------------
def test_url_handler(mocker):
    """Test url handler. Should detect youtube links accordingly."""

    url = "https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO"

    # Update mock
    message_mock = Mock()
    message_mock.text = url
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Context mock
    msg_mock = Mock()
    msg_mock.edit_text.return_value = None

    bot_mock = Mock()
    bot_mock.send_message.return_value = msg_mock

    context_mock = Mock()
    context_mock.bot = bot_mock

    # Youtube audio download mock
    youtube_track = YoutubeTrack("sample", "sample", "filepath", "audio/mpeg")
    download_youtube_audio_mock = Mock()
    download_youtube_audio_mock.return_value = youtube_track

    # Google drive mock
    drive_mock = Mock()

    mocker.patch.object(src.handlers, "download_youtube_audio", download_youtube_audio_mock)
    mocker.patch.object(src.handlers, "upload_to_drive", drive_mock)

    # Run #1
    url_handler(update_mock, context_mock)
    download_youtube_audio_mock.assert_called_once()
    drive_mock.assert_called_once()

    # Run #2

    url2 = "porter|https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO"

    message_mock = Mock()
    message_mock.text = url2
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    url_handler(update_mock, context_mock)
    download_youtube_audio_mock.assert_called()
    drive_mock.assert_called()


def test_url_handler_invalid_youtube_link(mocker):
    """Passed linked is invalid."""

    url_channel = "https://www.youtube.com/c/porterrobinson"

    # Update mock
    message_mock = Mock()
    message_mock.text = url_channel
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Context mock
    msg_mock = Mock()
    msg_mock.edit_text.return_value = None

    bot_mock = Mock()
    bot_mock.send_message.return_value = msg_mock

    context_mock = Mock()
    context_mock.bot = bot_mock

    # Youtube audio download mock
    youtube_track = YoutubeTrack("sample", "sample", "filepath", "audio/mpeg")
    download_youtube_audio_mock = Mock()
    download_youtube_audio_mock.return_value = youtube_track

    # Google drive mock
    drive_mock = Mock()

    mocker.patch.object(src.handlers, "download_youtube_audio", download_youtube_audio_mock)
    mocker.patch.object(src.handlers, "upload_to_drive", drive_mock)

    # Run
    url_handler(update_mock, context_mock)
    assert update_mock.message.reply_text.call_args[0][0] == "This URL does not point to a valid Youtube video ❌."


def test_url_handler_error_audio_download(mocker):
    """Errors on youtube audio download."""

    url = "https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO"

    # Update mock
    message_mock = Mock()
    message_mock.text = url
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Context mock
    msg_mock = Mock()
    msg_mock.edit_text.return_value = None

    bot_mock = Mock()
    bot_mock.send_message.return_value = msg_mock

    context_mock = Mock()
    context_mock.bot = bot_mock

    # Youtube audio download mock
    youtube_track = YoutubeTrack("sample", "sample", "filepath", "audio/mpeg")
    download_youtube_audio_mock = Mock()
    download_youtube_audio_mock.side_effect = YoutubeAudioDownloadFail

    # Google drive mock
    drive_mock = Mock()

    mocker.patch.object(src.handlers, "download_youtube_audio", download_youtube_audio_mock)
    mocker.patch.object(src.handlers, "upload_to_drive", drive_mock)

    # Run
    url_handler(update_mock, context_mock)
    assert msg_mock.edit_text.call_args[0][0] == "There was a problem downloading the audio from this Youtube link ❌."


def test_url_handler_drive_error(mocker):
    """Google drive error uploading."""

    url = "https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO"

    # Update mock
    message_mock = Mock()
    message_mock.text = url
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Context mock
    msg_mock = Mock()
    msg_mock.edit_text.return_value = None

    bot_mock = Mock()
    bot_mock.send_message.return_value = msg_mock

    context_mock = Mock()
    context_mock.bot = bot_mock

    # Youtube audio download mock
    youtube_track = YoutubeTrack("sample", "sample", "filepath", "audio/mpeg")
    download_youtube_audio_mock = Mock()
    download_youtube_audio_mock.return_value = youtube_track

    # Google drive mock
    drive_mock = Mock()
    drive_mock.side_effect = GoogleDriveUploadFail

    mocker.patch.object(src.handlers, "download_youtube_audio", download_youtube_audio_mock)
    mocker.patch.object(src.handlers, "upload_to_drive", drive_mock)

    # Run
    url_handler(update_mock, context_mock)
    assert msg_mock.edit_text.call_args[0][0] == "We managed to download the audio but failed to upload on Google Drive ❌."


def test_url_handler_unsupported_provider(mocker):
    """Unsupported provider."""

    url = "https://www.google.com"

    # Update mock
    message_mock = Mock()
    message_mock.text = url
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Context mock
    msg_mock = Mock()
    msg_mock.edit_text.return_value = None

    bot_mock = Mock()
    bot_mock.send_message.return_value = msg_mock

    context_mock = Mock()
    context_mock.bot = bot_mock

    # Youtube audio download mock
    youtube_track = YoutubeTrack("sample", "sample", "filepath", "audio/mpeg")
    download_youtube_audio_mock = Mock()
    download_youtube_audio_mock.return_value = youtube_track

    # Google drive mock
    drive_mock = Mock()
    drive_mock.side_effect = GoogleDriveUploadFail

    mocker.patch.object(src.handlers, "download_youtube_audio", download_youtube_audio_mock)
    mocker.patch.object(src.handlers, "upload_to_drive", drive_mock)

    # Run
    url_handler(update_mock, context_mock)
    assert update_mock.message.reply_text.call_args[0][0] == "We are yet to support URLs from this place 😕."
