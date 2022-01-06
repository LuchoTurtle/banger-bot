from __future__ import print_function

import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from definitions.definitions import AUTH_DIR

from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_creds():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(AUTH_DIR + 'token.json'):
        creds = Credentials.from_authorized_user_file(AUTH_DIR + 'token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                AUTH_DIR + 'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(AUTH_DIR + 'token.json', 'w') as token:
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

