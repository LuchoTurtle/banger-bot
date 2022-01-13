import pytest
from pytest_mock import MockerFixture
from unittest.mock import Mock, mock_open, patch
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta

from src.definitions.definitions import AUTH_DIR
from src.exceptions import GoogleDriveClientSecretNotFound
from src.services.gdrive import get_creds
import src.services.gdrive


def mocked_credentials(valid: bool = True, expired: bool = False, refresh_token="refresh_token_XX") -> Mock:
    """
    Creates a mock credentials object to be used.
    @param refresh_token: refresh token of the credential.
    @param expired: if the credential is expired or not
    @param valid: if the credential is to be valid or not.
    @return: parametrized Credentials object to be used as a mock object.
    """
    # Defining mocked credentials class returned when invoking "authorized_user_file" function
    mock_user_cred = Mock(spec=Credentials)
    mock_user_cred.client_id = "random_client_id",
    mock_user_cred.client_secret = "random_client_secret",
    mock_user_cred.expiry = datetime.now() + timedelta(days=1),
    mock_user_cred.refresh_token = refresh_token,
    mock_user_cred.scopes = ['https://www.googleapis.com/auth/drive'],
    mock_user_cred.token = "token_XX",
    mock_user_cred.token_uri = 'https://oauth2.googleapis.com/token',

    mock_user_cred.valid = valid
    mock_user_cred.expired = expired

    # Mocking methods to be used in functions
    mock = Mock(spec=Credentials)
    mock.from_authorized_user_file.return_value = mock_user_cred

    return mock


def mocked_flow() -> Mock:
    """
    Mocks Google auth flow object.
    @return:
    """
    # Defining main_flow, which returns a mock_flow which will return a credential object.
    mock_flow = Mock()
    main_flow = Mock()
    mock_cred = mocked_credentials()

    # Mocking methods to be used in functions
    mock_flow.run_local_server.return_value = mock_cred

    main_flow.from_client_secrets_file.return_value = mock_flow

    return main_flow


def test_clientsecret_not_found():
    """Erroring when paths do not point to a client secret and/or token json files."""
    with pytest.raises(GoogleDriveClientSecretNotFound):
        get_creds("", "")


def test_normal(mocker: MockerFixture):
    """Normal flow - checks if there's creds on the auth file and returns if positive. Auth directory is mocked."""

    # Setting mocks
    mock_cred = mocked_credentials()
    mocker.patch.object(src.services.gdrive, "Credentials", mock_cred)

    # Running and asserts
    creds = get_creds(AUTH_DIR, AUTH_DIR)

    assert creds.client_id == mock_cred.from_authorized_user_file().client_id
    assert creds.client_secret == mock_cred.from_authorized_user_file().client_secret
    assert creds.token == mock_cred.from_authorized_user_file().token
    assert creds.token_uri == mock_cred.from_authorized_user_file().token_uri
    assert creds.refresh_token == mock_cred.from_authorized_user_file().refresh_token


def test_creds_expired(mocker: MockerFixture):
    """Normal flow - sending expired credits and refresh is successful (should also write the refreshed token in the file - which is mocked)."""

    # Setting mocks
    mock_cred = mocked_credentials(valid=False, expired=True)
    mocker.patch.object(src.services.gdrive, "Credentials", mock_cred)

    # Running and asserts
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        creds = get_creds(AUTH_DIR, AUTH_DIR)

    assert creds.client_id == mock_cred.from_authorized_user_file().client_id
    assert creds.client_secret == mock_cred.from_authorized_user_file().client_secret
    assert creds.token == mock_cred.from_authorized_user_file().token
    assert creds.token_uri == mock_cred.from_authorized_user_file().token_uri
    assert creds.refresh_token == mock_cred.from_authorized_user_file().refresh_token
    # Check if the returned credentials after invoking 'from_authorized_user_file' has been refreshed
    mock_cred.from_authorized_user_file().refresh.assert_called_once()


def test_creds_relogin(mocker: MockerFixture):
    """The credentials are not valid and need user to login again. The user interaction is mocked."""

    # Setting mocks
    mock_flow = mocked_flow()
    mock_cred = mocked_credentials(valid=False, expired=False, refresh_token=None)
    mocker.patch.object(src.services.gdrive, "InstalledAppFlow", mock_flow)
    mocker.patch.object(src.services.gdrive, "Credentials", mock_cred)

    # Running and asserts
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        creds = get_creds(AUTH_DIR, AUTH_DIR)


    assert creds.from_authorized_user_file().client_id == mock_cred.from_authorized_user_file().client_id
    assert creds.from_authorized_user_file().client_secret == mock_cred.from_authorized_user_file().client_secret
    assert creds.from_authorized_user_file().token == mock_cred.from_authorized_user_file().token
    assert creds.from_authorized_user_file().token_uri == mock_cred.from_authorized_user_file().token_uri
    # Check if the flow methods have been called
    mock_flow.from_client_secrets_file.assert_called_once()
    mock_flow.from_client_secrets_file().run_local_server.assert_called_once()
