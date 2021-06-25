from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaFileUpload
import os

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
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def upload_to_drive(file_location, filename, mime_type):
    # Get driver service to upload the file
    service = build('drive', 'v3', credentials=get_creds(), cache_discovery=False)

    metadata = {'name': filename}
    media = MediaFileUpload(file_location, chunksize=1024 * 1024, mimetype=mime_type, resumable=True)

    # Upload file
    request = service.files().create(body=metadata,
                                     media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))


def file_handler(update, context):
    """handles the uploaded files"""

    filename = update.message.audio.title
    file_location = '../files/' + filename
    mime_type = update.message.audio.mime_type

    # Get file info
    file = context.bot.getFile(update.message.audio.file_id)
    file.download(file_location)

    upload_to_drive(file_location, filename, mime_type)

    # Send confirmation to bot user
    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ File uploaded!")

    # Delete uplodaded file locally
    # os.remove('./' + filename)
