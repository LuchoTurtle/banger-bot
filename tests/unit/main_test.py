from unittest.mock import Mock

import src.main
from src.main import start, help_command, url_handler


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

    # Callback mockmoc
    callback_mock = Mock()

    mocker.patch.object(src.main, "youtube_callback", youtube_callback)

    url_handler(update_mock, callback_mock)

    # Assertions
    assert "We are yet to support URLs from this place." in update_mock.message.reply_text.call_args[0][0]



