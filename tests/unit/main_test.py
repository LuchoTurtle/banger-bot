from unittest.mock import Mock
import pytest

import src.main
from src.exceptions import TrackNotFound
from src.models import File, Action, ShazamTrack
from src.main import start, help_command, url_handler, audio_file_handler_button, audio_file_handler


def test_start():
    """Test start command replies to message"""

    # Update mock
    message_mock = Mock()
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Callback mock
    callback_mock = Mock()

    start(update_mock, callback_mock)

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

    help_command(update_mock, callback_mock)

    assert update_mock.message.reply_text.called is True
    assert "help" in update_mock.message.reply_text.call_args[0][0]


def test_url_handler(mocker):
    """Test url handler. Should detect youtube links accordingly."""

    url = "https://www.youtube.com/watch?v=W2TE0DjdNqI&ab_channel=PorterRobinsonVEVO"

    # Update mock
    message_mock = Mock()
    message_mock.text = url
    message_mock.reply_text.return_value = None

    update_mock = Mock()
    update_mock.message = message_mock

    # Youtube callback
    youtube_callback = Mock()

    # Callback mockmoc
    callback_mock = Mock()

    mocker.patch.object(src.main, "youtube_callback", youtube_callback)

    url_handler(update_mock, callback_mock)

    # Assertions
    youtube_callback.assert_called_once()


def test_url_handler_invalid(mocker):
    """Test url handler. Errors because the link is not supported."""

    url = "https://www.google.com/"

    # Update mock
    message_mock = Mock()
    message_mock.text = url

    update_mock = Mock()
    update_mock.message = message_mock

    # Youtube callback
    youtube_callback = Mock()

    # Callback mock
    callback_mock = Mock()

    mocker.patch.object(src.main, "youtube_callback", youtube_callback)

    url_handler(update_mock, callback_mock)

    # Assertions
    assert "We are yet to support URLs from this place." in update_mock.message.reply_text.call_args[0][0]


def test_audio_file_handler_button_shazam(mocker):
    """Test callback handler when user presses button when file is sent (for Shazam)"""

    file: File = File(Action.SHAZAM,
                      "sample.mp3",
                      "12345",
                      "mpeg/audio",
                      "15552")

    return_track: ShazamTrack = ShazamTrack({
        "track": {
            "title": 'Goodbye To A World',
            "subtitle": 'Porter Robinson',
            "images": {
                "coverarthq": "www.randomurl.com"
            },
            "hub": {
                "providers": [
                    {
                        "caption": "randomcaption",
                        "actions": [
                            {
                                "uri": "randomuri"
                            }
                        ]
                    }
                ]
            }
        },
    })

    # Context mock
    context_file_mock = Mock()
    context_file_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.send_photo.return_value = None
    bot_mock.getFile.return_value = context_file_mock

    callback_mock = Mock()
    callback_mock.bot = bot_mock

    # Updater mock
    query_mock = Mock()
    query_mock.answer.return_value = None
    query_mock.data = file
    query_mock.edit_message_text.return_value = None

    update_mock = Mock()
    update_mock.callback_query = query_mock

    # Asyncio mock
    asyncio_mock = Mock()
    asyncio_mock.run.return_value = return_track

    mocker.patch.object(src.main, "asyncio", asyncio_mock)

    audio_file_handler_button(update_mock, callback_mock)

    # Assertions
    asyncio_mock.run.assert_called_once()
    assert "found a track" in query_mock.edit_message_text.call_args[0][0]


def test_audio_file_handler_button_shazam_error(mocker):
    """Errors because track couldn't be found."""

    file: File = File(Action.SHAZAM,
                      "sample.mp3",
                      "12345",
                      "mpeg/audio",
                      "15552")

    return_track: ShazamTrack = ShazamTrack({
        "track": {
            "title": 'Goodbye To A World',
            "subtitle": 'Porter Robinson',
            "images": {
                "coverarthq": "www.randomurl.com"
            },
            "hub": {
                "providers": [
                    {
                        "caption": "randomcaption",
                        "actions": [
                            {
                                "uri": "randomuri"
                            }
                        ]
                    }
                ]
            }
        },
    })

    # Context mock
    context_file_mock = Mock()
    context_file_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.send_photo.return_value = None
    bot_mock.getFile.return_value = context_file_mock

    callback_mock = Mock()
    callback_mock.bot = bot_mock

    # Updater mock
    query_mock = Mock()
    query_mock.answer.return_value = None
    query_mock.data = file
    query_mock.edit_message_text.return_value = None

    update_mock = Mock()
    update_mock.callback_query = query_mock

    # Asyncio mock
    asyncio_mock = Mock()
    asyncio_mock.run.side_effect = TrackNotFound

    mocker.patch.object(src.main, "asyncio", asyncio_mock)

    audio_file_handler_button(update_mock, callback_mock)

    # Asserts
    asyncio_mock.run.assert_called_once()
    assert "Unfortunately we couldn\'t detect a song" in query_mock.edit_message_text.call_args[0][0]


def test_audio_file_handler_button_google_drive(mocker):
    """Tests when Google Drive button is pressed."""

    file: File = File(Action.GDRIVE_UPLOAD,
                      "sample.mp3",
                      "12345",
                      "mpeg/audio",
                      "15552")

    # Context mock
    context_file_mock = Mock()
    context_file_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.send_photo.return_value = None
    bot_mock.getFile.return_value = context_file_mock

    callback_mock = Mock()
    callback_mock.bot = bot_mock

    # Updater mock
    query_mock = Mock()
    query_mock.answer.return_value = None
    query_mock.data = file
    query_mock.edit_message_text.return_value = None

    update_mock = Mock()
    update_mock.callback_query = query_mock

    # Google drive
    upload_to_drive_mock = Mock()

    mocker.patch.object(src.main, "upload_to_drive", upload_to_drive_mock)

    audio_file_handler_button(update_mock, callback_mock)

    # Asserts
    upload_to_drive_mock.assert_called_once()


def test_audio_file_handler_button_action_not_permitted(mocker):
    """Tests when unauthorized action is made.."""

    file: File = File("random_action",
                      "sample.mp3",
                      "12345",
                      "mpeg/audio",
                      "15552")

    # Context mock
    context_file_mock = Mock()
    context_file_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.send_photo.return_value = None
    bot_mock.getFile.return_value = context_file_mock

    callback_mock = Mock()
    callback_mock.bot = bot_mock

    # Updater mock
    query_mock = Mock()
    query_mock.answer.return_value = None
    query_mock.data = file
    query_mock.edit_message_text.return_value = None

    update_mock = Mock()
    update_mock.callback_query = query_mock

    audio_file_handler_button(update_mock, callback_mock)

    # Asserts
    assert "That action is not permitted" in query_mock.edit_message_text.call_args[0][0]


def test_audio_file_handler_voice(mocker):
    """Tests when a voice audio is sent and handled."""

    # Updater mock
    audio_mock = Mock()
    audio_mock.title = "title"
    audio_mock.file_id = "file_id"
    audio_mock.mime_type = "mime_type"

    message_mock = Mock()
    message_mock.audio = audio_mock
    message_mock.reply_text.return_value = None

    effective_chat_mock = Mock()
    effective_chat_mock.id = "id"

    update_mock = Mock()
    update_mock.message = message_mock
    update_mock.effective_chat = effective_chat_mock

    # Callback mock
    callback_mock = Mock()

    audio_file_handler(update_mock, callback_mock)

    # Asserts
    message_mock.reply_text.assert_called_once()


def test_audio_file_handler_audio(mocker):
    """Tests when an audio file is sent and handled."""

    # Updater mock
    voice_mock = Mock()
    voice_mock.file_unique_id = "file_unique_id"
    voice_mock.file_id = "file_id"
    voice_mock.mime_type = "mime_type"

    message_mock = Mock()
    message_mock.voice = voice_mock
    message_mock.reply_text.return_value = None

    effective_chat_mock = Mock()
    effective_chat_mock.id = "id"

    update_mock = Mock()
    update_mock.message = message_mock
    update_mock.effective_chat = effective_chat_mock

    # Callback mock
    callback_mock = Mock()

    audio_file_handler(update_mock, callback_mock)

    # Asserts
    message_mock.reply_text.assert_called_once()


def test_audio_file_handler_none(mocker):
    """Tests when not voice nor audio file are sent."""

    # Updater mock

    message_mock = Mock()
    message_mock.voice = None
    message_mock.audio = None
    message_mock.reply_text.return_value = None

    effective_chat_mock = Mock()
    effective_chat_mock.id = "id"

    update_mock = Mock()
    update_mock.message = message_mock
    update_mock.effective_chat = effective_chat_mock

    # Callback mock
    callback_mock = Mock()

    audio_file_handler(update_mock, callback_mock)

    # Asserts
    assert message_mock.reply_text.called is not True
