from unittest.mock import Mock

from src.main import start_handler, help_handler


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