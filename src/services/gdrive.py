from __future__ import print_function

import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from telegram import Message
from telegram.constants import ParseMode


from src.definitions.definitions import AUTH_DIR

from googleapiclient.http import MediaFileUpload

from src.exceptions import GoogleDriveClientSecretNotFound, FileDoesNotExist, GoogleDriveInvalidFileMeta, \
    GoogleDriveUploadFail, GoogleDriveCreateFolderFail

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


def create_drive_folder(folder_name: str, parent_id=None):
    """
    Creates a new folder on Google Drive with the given name
    @param folder_name: the name of the folder to be created.
    @param parent_id: the folder parent ID if we want to create a folder inside a folder.
    @return: ID of the newly created server
    """

    try:
        service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

        file_metadata = {
            'name': folder_name,
            'mimeType': "application/vnd.google-apps.folder"
        }
        if parent_id:
            file_metadata['parents'] = [{'id': parent_id}]

        root_folder = service.files().create(body=file_metadata).execute()

    except Exception as e:
        raise GoogleDriveCreateFolderFail

    return root_folder['id']


def get_drive_folder(folder_name: str):
    """
    Fetches the ID of the Google Drive folder of the given name.
    @param folder_name: name of the folder we're looking for
    @return: ID of the folder. Returns None if no folder was found.
    """

    if folder_name is None:
        return None

    service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

    folder_id = None
    page_token = None
    while True and folder_id is None:
        response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()

        for file in response.get('files', []):

            if file.get('name') == folder_name:
                folder_id = file.get('id')
                break

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return folder_id


async def upload_to_drive(file_path: str, file_title: str, file_mime_type: str, message: Message,
                    destination_folder: str = None):
    """
    Uploads file from 'file_path' to google drive on a given destination folder. If no destination folder is given, it uploads to root Google Drive folder.
    If the folder is given and not created on Google Drive, it's created before upload.
    Telegram message is passed to update the progress whilst uploading.
    @param file_path: path to the file to be uploaded.
    @param file_title: title of the file.
    @param file_mime_type: mimetype of the file.
    @param message: Telegram message object.
    @param destination_folder: Drive destination folder.
    @return:
    """

    # Verifying params
    if not os.path.exists(file_path):
        raise FileDoesNotExist

    if len(file_title) == 0 or len(file_mime_type) == 0:
        raise GoogleDriveInvalidFileMeta

    try:
        service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

        # If a destination folder is passed, we check if it exists. If not, we just push to the root directory
        if destination_folder:
            # Check if folder exists. If it does, use the ID to create folder. If not, we create a new folder
            folder_id = get_drive_folder(destination_folder)

            if folder_id is None:
                folder_id = create_drive_folder(destination_folder)

        if destination_folder:
            metadata = {
                'name': file_title,
                'parents': [folder_id]
            }
        else:
            metadata = {
                'name': file_title
            }

        # Upload file
        media = MediaFileUpload(file_path, chunksize=1024 * 1024, mimetype=file_mime_type, resumable=True)
        request = service.files().create(body=metadata,
                                         media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                await message.edit_text(
                    "Got it! Going to download the file now and try to upload it to Google Drive. Gimme a few seconds ⌛!\n"
                    "Uploading to Google Drive: " + str(progress) + "%",
                    parse_mode=ParseMode.MARKDOWN)

        # Release media stream to so the process can delete it afterwards
        media.stream().close()

        # Notify user upload is complete
        await message.edit_text(
            "Got it! Going to download the file now and try to upload it to Google Drive. Gimme a few seconds ⌛!\n"
            "Uploading to Google Drive complete!",
            parse_mode=ParseMode.MARKDOWN)

        # Delete uploaded file locally
        os.remove(file_path)

    except Exception as e:
        raise GoogleDriveUploadFail("Problem uploading file to Google Drive.")
