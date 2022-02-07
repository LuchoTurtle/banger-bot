from unittest.mock import Mock
import pytest
from telegram.ext import (
    CallbackContext
)
import src.services.youtube
from src.services.youtube import url_is_valid, youtube_callback

# URLV is valid -----------------
def test_url_is_valid():
    """URL passed is valid"""

    bot_mock = Mock()
    bot_mock.send_message.return_value = None

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    ret = url_is_valid(None, mock_context, "https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15")

    assert ret


def test_url_is_invalid():
    """URL passed is invalid"""

    # Context mock
    bot_mock = Mock()
    bot_mock.send_message.return_value = None

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    # Update mock
    effective_chat_mock = Mock()
    effective_chat_mock.id.return_value = 12354

    update_mock = Mock()
    update_mock.effective_chat.return_value = effective_chat_mock

    ret = url_is_valid(update_mock, mock_context, "https://www.youtube.com/c/porterrobinson")
    assert not ret

    ret = url_is_valid(update_mock, mock_context, "https://www.google.com")
    assert not ret


# Youtube callback --------------------
def test_callback_normal(mocker):
    """Normal callback behaviour"""

    # Mock context
    bot_mock = Mock()
    bot_mock.send_message.return_value = None

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    # Youtube
    ydl_mock = Mock()
    ydl_mock.extract_info.return_value = {
        "title": "sample",
        "id": "sample"
    }

    # Update mock
    effective_chat_mock = Mock()
    effective_chat_mock.id.return_value = 12354

    update_mock = Mock()
    update_mock.effective_chat.return_value = effective_chat_mock

    # Google drive mock
    drive = Mock()

    # Mock and execute the function
    mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.return_value = ydl_mock
    mocker.patch.object(src.services.youtube, "upload_to_drive", drive)

    youtube_callback(update_mock, mock_context, "https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15")

    # Asserts
    ydl_mock.extract_info.assert_called_once()
    drive.assert_called_once()


def test_error_downloading(mocker):
    """Errors because there was a problem downloading Youtube file"""

    # Mock context
    bot_mock = Mock()
    bot_mock.send_message.return_value = None

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    # Youtube
    ydl_mock = Mock()
    ydl_mock.extract_info.return_value = {
        "title": "sample",
        "id": "sample"
    }

    # Update mock
    effective_chat_mock = Mock()
    effective_chat_mock.id.return_value = 12354

    update_mock = Mock()
    update_mock.effective_chat.return_value = effective_chat_mock

    # Google drive mock
    drive = Mock()

    mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.side_effect = Exception
    mocker.patch.object(src.services.youtube, "upload_to_drive", drive)

    youtube_callback(update_mock, mock_context, "https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15")

    assert mock_context.bot.send_message.call_args[1]['text'] == "There was an error downloading this Youtube video ❌.\nHave you checked if it's available? 🤔"


def test_error_uploading_to_drive(mocker):
    """Errors because there was a problem uploading Youtube song to drive"""

    # Mock context
    bot_mock = Mock()
    bot_mock.send_message.return_value = None

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    # Youtube
    ydl_mock = Mock()
    ydl_mock.extract_info.return_value = {
        "title": "sample",
        "id": "sample"
    }

    # Update mock
    effective_chat_mock = Mock()
    effective_chat_mock.id.return_value = 12354

    update_mock = Mock()
    update_mock.effective_chat.return_value = effective_chat_mock

    # Google drive mock
    drive = Mock(side_effect=Exception)

    mocker.patch('youtube_dl.YoutubeDL').return_value.__enter__.return_value = ydl_mock
    mocker.patch.object(src.services.youtube, "upload_to_drive", drive)

    youtube_callback(update_mock, mock_context, "https://www.youtube.com/watch?v=cdHdPu4JqSE&list=RDrtoBmxLCGek&index=15")

    assert mock_context.bot.send_message.call_args[1]['text'] == "There was an error uploading this file to Google Drive ❌.\nHave you set up everything correctly? 🤔"
