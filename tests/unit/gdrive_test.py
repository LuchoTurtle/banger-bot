import pytest
from pytest_mock import MockerFixture
from unittest.mock import Mock, mock_open, patch
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta

from src.definitions.definitions import AUTH_DIR
from src.exceptions import GoogleDriveClientSecretNotFound, FileDoesNotExist, GoogleDriveInvalidFileMeta, \
    GoogleDriveUploadFail
from src.services.gdrive import get_creds, upload_to_drive
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
    @return: mocked Google auth flow object.
    """
    # Defining main_flow, which returns a mock_flow which will return a credential object.
    mock_flow = Mock()
    main_flow = Mock()
    mock_cred = mocked_credentials()

    # Mocking methods to be used in functions
    mock_flow.run_local_server.return_value = mock_cred

    main_flow.from_client_secrets_file.return_value = mock_flow

    return main_flow


def mocked_build() -> Mock:
    """
    Mocks Google service upload object.
    @return: mocked Google service upload object.
    """
    mock_request = Mock()
    mock_request.next_chunk.return_value = ("status", "response")

    mock_service_files = Mock()
    mock_service_files.create.return_value = mock_request

    mock_service = Mock()
    mock_service.files.return_value = mock_service_files

    mock_build = Mock()
    mock_build.return_value = mock_service

    return mock_build


def mocked_media() -> Mock:
    """
    Mocks Google media upload object.
    @return: mocked Google media upload object.
    """
    mock_media = Mock(spec=MediaFileUpload)
    mock_media.stream.close.return_value = None

    mock_media_file_upload = Mock(return_value=mock_media)

    return mock_media_file_upload


# Get credentials --------------------------------------

def test_clientsecret_not_found():
    """Erroring when paths do not point to a client secret and/or token json files."""
    with pytest.raises(GoogleDriveClientSecretNotFound):
        get_creds("", "")


def test_creds_normal(mocker: MockerFixture):
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


# Upload to drive --------------------------------------

def test_upload_file_not_found():
    """Erroring when given file path does not point to a valid object."""
    with pytest.raises(FileDoesNotExist):
        upload_to_drive("", "", "")


def test_upload_filemeta_invalid():
    """Erroring when given file metadata are empty."""
    with pytest.raises(GoogleDriveInvalidFileMeta):
        upload_to_drive(AUTH_DIR, "", "")


def test_upload_file_error(mocker):
    """Erroring when given there was trouble uploading file."""
    mock_build = mocked_build()
    mock_media = mocked_media()
    mock_build.side_effect = Exception("fail")
    mock_media.side_effect = Exception("fail")
    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "MediaFileUpload", mock_media)

    with pytest.raises(GoogleDriveUploadFail):
        upload_to_drive(AUTH_DIR, "test_file", "audio/mpeg")


def test_upload_file_normal(mocker: MockerFixture):
    """Normal flow - uploads file to Google Drive."""

    # Setting mocks
    mock_build = mocked_build()
    mock_media = mocked_media()
    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "MediaFileUpload", mock_media)

    # Running and asserts
    with patch("os.remove"):
        upload_to_drive(AUTH_DIR, "mo_bamba", "audio/mpeg")

    mock_build.assert_called_once()
    mock_media.assert_called_once()
    mock_build.return_value.files.assert_called_once()
    mock_build.return_value.files.return_value.create.assert_called_once()
    mock_build.return_value.files.return_value.create.return_value.next_chunk.assert_called_once()
    mock_media.return_value.stream.assert_called_once()
    mock_media.return_value.stream.return_value.close.assert_called_once()
