import asyncio

import pytest
from unittest.mock import Mock, patch

import src.services.shazam
from src.exceptions import RemoveFileFailed, TrackNotFound
from src.services.shazam import shazam
from src.models import File, Action, ShazamTrack
from telegram.ext import (
    CallbackContext
)


def test_normal():
    """Normal behaviour - receives the path of a file and checks it on Shazam."""

    file_obj = File(
        action=Action.GDRIVE_UPLOAD,
        file_title="sample.mp3",
        file_id="19029395",
        mime_type="audio/mpeg",
        chat_id="81298222"
    )

    file_obj_mock = Mock()
    file_obj_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.getFile.return_value = file_obj_mock

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    with patch("os.remove"):
        track: ShazamTrack = asyncio.run(
            shazam(file_obj, mock_context)
        )

    assert track.title == 'Goodbye To A World'
    assert track.subtitle == 'Porter Robinson'
    assert track.image is not None
    assert track.first_provider is not None


def test_file_not_found():
    """Erroring because file is not found."""

    file_obj = File(
        action=Action.GDRIVE_UPLOAD,
        file_title="notfoundfile",
        file_id="19029395",
        mime_type="audio/mpeg",
        chat_id="81298222"
    )

    file_obj_mock = Mock()
    file_obj_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.getFile.return_value = file_obj_mock

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    with pytest.raises(FileNotFoundError):
        track: ShazamTrack = asyncio.run(
            shazam(file_obj, mock_context)
        )


def test_error_removing_file(mocker):
    """Erroring because file could not be removed after Shazaming."""

    file_obj = File(
        action=Action.GDRIVE_UPLOAD,
        file_title="sample.mp3",
        file_id="19029395",
        mime_type="audio/mpeg",
        chat_id="81298222"
    )

    file_obj_mock = Mock()
    file_obj_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.getFile.return_value = file_obj_mock

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    os_mock = Mock()
    os_mock.remove.side_effect = Exception

    mocker.patch.object(src.services.shazam, 'os', os_mock)

    with pytest.raises(RemoveFileFailed):
        with patch("os.remove"):
            track: ShazamTrack = asyncio.run(
                shazam(file_obj, mock_context)
            )


def test_error_while_serializing_track(mocker):
    """Erroring because file could not be serialized after Shazaming."""

    file_obj = File(
        action=Action.GDRIVE_UPLOAD,
        file_title="sample.mp3",
        file_id="19029395",
        mime_type="audio/mpeg",
        chat_id="81298222"
    )

    file_obj_mock = Mock()
    file_obj_mock.download.return_value = None

    bot_mock = Mock()
    bot_mock.getFile.return_value = file_obj_mock

    mock_context = Mock(spec=CallbackContext)
    mock_context.bot.return_value = bot_mock

    shazam_track_mock = Mock()
    shazam_track_mock.side_effect = TrackNotFound

    mocker.patch.object(src.services.shazam, 'ShazamTrack', shazam_track_mock)

    with pytest.raises(TrackNotFound):
        with patch("os.remove"):
            track: ShazamTrack = asyncio.run(
                shazam(file_obj, mock_context)
            )


