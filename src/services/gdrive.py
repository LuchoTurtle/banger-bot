from __future__ import print_function

import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from src.definitions.definitions import AUTH_DIR

from googleapiclient.http import MediaFileUpload

from src.exceptions import GoogleDriveClientSecretNotFound

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_creds(token_path=AUTH_DIR + 'token.json', client_secrets_path=AUTH_DIR + 'client_secrets.json'):
    """
    Gets the user Google Drive credentials. It's expecting a json file with the client secrets of the Google application.
    This function creates a 'token.json' file that has a token and a refresh token so the user only has to authorize once.
    @param token_path: token json file path (which has the token and refresh token).
    @param client_secrets_path: Google client secrets json file path.
    @return: Google credentials object.
    """

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(client_secrets_path):
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
                creds = flow.run_local_server(port=8080)
            else:
                raise GoogleDriveClientSecretNotFound("Couldn't find client secrets json file in this directory.")

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def upload_to_drive(file_path: str, file_title: str, file_mime_type: str):
    try:
        service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

        metadata = {'name': file_title}
        media = MediaFileUpload(file_path, chunksize=1024 * 1024, mimetype=file_mime_type, resumable=True)

        # Upload file
        request = service.files().create(body=metadata,
                                         media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print("Uploaded %d%%." % int(status.progress() * 100))

        # Release media stream to so the process can delete it afterwards
        media.stream().close()

        # Delete uploaded file locally
        os.remove(file_path)

    except Exception as e:
        raise Exception("Problem uploading file to Google Drive.")
