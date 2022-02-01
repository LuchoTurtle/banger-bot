# Setting up your Google Drive account to store your music :musical_note:

You need a Google Drive account for the files to be stored. For this, do the following:

### 1 - Create a project on Google Cloud
You need to create a project on Google Cloud. The process is painless and quite easy to follow through.
Check [this link](https://developers.google.com/workspace/guides/create-project) to create a basic project.

### 2 - Activate Google Drive API on the API Library within the Google Cloud Platform
After entering your newly created project, you might notice a "**Library**" button on the sidebar to your left.
Click on it, search for the "Google Drive API" and activate it.

### 3 - Setting up OAuth Consent Screen
On the same sidebar, follow the OAuth Consent Screen wizard. Keep in mind two things:
* In the **Scopes** section, add the following. These will allow the Bot to upload the files in your Google Drive.
    * `/auth/drive.metadata.readonly`
    * `/auth/drive`
* In the **Test Users**, add the e-mail of your Google account.

### 4 - Create credentials
You need to create credentials now. Go to the **Credentials** sidebar menu and create a "OAuth Client ID" credential.

* Choose the `Web Application` application type.

* Add `http://localhost:8080` (or the URI of the machine you're hosting in) to **Authorized JavaScript origins**.

* Add `http://localhost:8080/` (or the URI of the machine you're hosting in) to **Authorized redirect URIs**.


Save your changes and you should be sorted! Give yourself a pat on the back :tada:

### 5 - Download the `.json` credential file
Download your credential `.json` file and paste it in the `src/auth` directory and change its name to `client_secrets.json`.
When you run the bot for the first time, it will prompt you to login the e-mail associated with your Google Drive and it will create a `token.json` file to be used on recurrent sessions.
