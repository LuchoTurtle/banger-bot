from src.exceptions import GoogleDriveClientSecretNotFound
from src.services.gdrive import get_creds
import src.services.gdrive
import pytest
from datetime import datetime, timedelta

from unittest.mock import Mock
from google.oauth2.credentials import Credentials

credentials_class_object = Credentials(
    client_id="random_client_id",
    client_secret="random_client_secret",
    expiry=datetime.now() + timedelta(days=1),
    refresh_token="refresh_token_XX",
    scopes=['https://www.googleapis.com/auth/drive'],
    token="token_XX",
    token_uri='https://oauth2.googleapis.com/token',
)


def test_clientsecret_not_found():
    """Erroring when paths do not point to a client secret and/or token json files."""
    with pytest.raises(GoogleDriveClientSecretNotFound):
        get_creds("", "")


def test_normal(mocker):
    """Normal flow"""
    credentials_mock = Mock(spec=Credentials)
    credentials_mock.from_authorized_user_file.return_value = credentials_class_object

    mocker.patch.object(src.services.gdrive, "Credentials", credentials_mock)

    creds = get_creds()

    assert creds.client_id == credentials_class_object.client_id
    assert creds.client_secret == credentials_class_object.client_secret
    assert creds.token == credentials_class_object.token
    assert creds.token_uri == credentials_class_object.token_uri


#https://stackoverflow.com/questions/57808461/how-to-mock-a-google-api-library-with-python-3-7-for-unit-testing