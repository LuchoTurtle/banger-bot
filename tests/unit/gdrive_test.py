import pytest
from pytest_mock import MockerFixture
from unittest.mock import Mock, mock_open, patch
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta

from src.definitions.definitions import AUTH_DIR
from src.exceptions import GoogleDriveClientSecretNotFound, FileDoesNotExist, GoogleDriveInvalidFileMeta, \
    GoogleDriveUploadFail, GoogleDriveCreateFolderFail
from src.services.gdrive import get_creds, upload_to_drive, create_drive_folder, get_drive_folder
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
    status_mock = Mock()
    status_mock.progress.return_value = 0.1

    mock_request = Mock()
    mock_request.next_chunk.return_value = (status_mock, "response")
    mock_request.execute.return_value = {
        'id': "random_folder_id_123"
    }

    execute_mock = Mock()
    execute_mock.execute.return_value = {
        'files': [{
            "name": "folder_name",
            "id": "folder_id"
        }],
        'nextPageToken': None
    }

    mock_service_files = Mock()
    mock_service_files.create.return_value = mock_request
    mock_service_files.list.return_value = execute_mock

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

    mock_message = Mock()
    with pytest.raises(FileDoesNotExist):
        upload_to_drive("", "", mock_message, "")


def test_upload_filemeta_invalid():
    """Erroring when given file metadata are empty."""

    mock_message = Mock()
    with pytest.raises(GoogleDriveInvalidFileMeta):
        upload_to_drive(AUTH_DIR, "", mock_message, "")


def test_upload_file_error(mocker):
    """Erroring when given there was trouble uploading file."""
    mock_build = mocked_build()
    mock_media = mocked_media()
    mock_build.side_effect = Exception("fail")
    mock_media.side_effect = Exception("fail")
    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "MediaFileUpload", mock_media)
    mock_message = Mock()

    with pytest.raises(GoogleDriveUploadFail):
        upload_to_drive(AUTH_DIR, "test_file", "audio/mpeg", mock_message)


def test_upload_file_normal(mocker: MockerFixture):
    """Normal flow - uploads file to Google Drive."""

    # Setting mocks
    mock_build = mocked_build()
    mock_media = mocked_media()
    mock_create_folder = Mock()
    mock_create_folder.return_value = "id_123"
    mock_get_drive_folder = Mock()
    mock_get_drive_folder.return_value = "id_123"
    mock_message = Mock()

    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "MediaFileUpload", mock_media)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())
    mocker.patch.object(src.services.gdrive, "create_drive_folder", mock_create_folder)
    mocker.patch.object(src.services.gdrive, "get_drive_folder", mock_get_drive_folder)

    # Running and asserts
    with patch("os.remove"):
        upload_to_drive(AUTH_DIR, "mo_bamba", "audio/mpeg", mock_message)

    mock_build.assert_called_once()
    mock_media.assert_called_once()
    mock_build.return_value.files.assert_called_once()
    mock_build.return_value.files.return_value.create.assert_called_once()
    mock_build.return_value.files.return_value.create.return_value.next_chunk.assert_called_once()
    mock_media.return_value.stream.assert_called_once()
    mock_media.return_value.stream.return_value.close.assert_called_once()
    mock_message.edit_text.assert_called()


def test_upload_file_normal_create_folder(mocker: MockerFixture):
    """Normal flow - uploads file to Google Drive (and creates folder along the way)"""

    # Setting mocks
    mock_build = mocked_build()
    mock_media = mocked_media()
    mock_create_folder = Mock()
    mock_create_folder.return_value = "id_123"
    mock_get_drive_folder = Mock()
    mock_get_drive_folder.return_value = None
    mock_message = Mock()

    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "MediaFileUpload", mock_media)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())
    mocker.patch.object(src.services.gdrive, "create_drive_folder", mock_create_folder)
    mocker.patch.object(src.services.gdrive, "get_drive_folder", mock_get_drive_folder)

    # Running and asserts
    with patch("os.remove"):
        upload_to_drive(AUTH_DIR, "mo_bamba", "audio/mpeg", mock_message, destination_folder="tag")

    mock_build.assert_called_once()
    mock_media.assert_called_once()
    mock_build.return_value.files.assert_called_once()
    mock_build.return_value.files.return_value.create.assert_called_once()
    mock_build.return_value.files.return_value.create.return_value.next_chunk.assert_called_once()
    mock_media.return_value.stream.assert_called_once()
    mock_media.return_value.stream.return_value.close.assert_called_once()
    mock_create_folder.assert_called_once()
    mock_message.edit_text.assert_called()


# Create folder --------------------------------------
def test_create_folder(mocker: MockerFixture):
    """Normal flow - creates a new folder without parent"""

    # Setting mocks
    mock_build = mocked_build()

    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())

    # Running and asserts
    folder_id = create_drive_folder("random_folder_name")

    mock_build.assert_called_once()
    assert folder_id == "random_folder_id_123"


def test_create_folder_with_parentId(mocker: MockerFixture):
    """Normal flow - creates a new folder without parent"""

    # Setting mocks
    mock_build = mocked_build()

    mocker.patch.object(src.services.gdrive, "build", mock_build)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())

    # Running and asserts
    folder_id = create_drive_folder("random_folder_name", "parentId")

    mock_build.assert_called_once()
    assert folder_id == "random_folder_id_123"


def test_error_creating_folder(mocker: MockerFixture):
    """Raises exception because there was an error creating a folder."""

    mock_build = mocked_build()
    mock_build.side_effect = Exception("fail")
    mocker.patch.object(src.services.gdrive, "build", mock_build)

    with pytest.raises(GoogleDriveCreateFolderFail):
        create_drive_folder("random_folder_name")


# Get folder --------------------------------------
def test_get_drive_folder(mocker: MockerFixture):
    """Normal flow - getting the drive folder name."""

    # Setting mocks
    build_mock = mocked_build()

    mocker.patch.object(src.services.gdrive, "build", build_mock)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())

    # Running and asserts
    folder_id = get_drive_folder("folder_name")

    assert folder_id == "folder_id"


def test_get_drive_folder_not_found(mocker: MockerFixture):
    """Normal flow - not finding the folder with the name."""

    # Setting mocks
    build_mock = mocked_build()

    mocker.patch.object(src.services.gdrive, "build", build_mock)
    mocker.patch.object(src.services.gdrive, "get_creds", Mock())

    # Running and asserts
    folder_id = get_drive_folder("not_found")

    assert folder_id is None
