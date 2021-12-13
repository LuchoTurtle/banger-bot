from __future__ import print_function

import os.path
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from definitions import ROOT_DIR

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
    if os.path.exists('../auth/token.json'):
        creds = Credentials.from_authorized_user_file('../auth/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ROOT_DIR + '/auth/client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(ROOT_DIR + '/auth/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def upload_to_drive(file_id, file_location, title, mime_type, context):

    file = context.bot.getFile(file_id)
    file.download(file_location)

    try:
        # Get driver service to upload the file
        service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

        metadata = {'name': title}
        media = MediaFileUpload(file_location, chunksize=1024 * 1024, mimetype=mime_type, resumable=True)

        # Upload file
        request = service.files().create(body=metadata,
                                         media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print("Uploaded %d%%." % int(status.progress() * 100))

    except Exception as e:
        raise Exception("Problem uploading file to Google Drive.")

    # Delete uploaded file locally
    # os.remove('./' + filename)
