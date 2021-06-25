<p align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="./docs/logo.png" alt="Logo" >
  </a>

  <h3 align="center">Banger Bot</h3>

  <p align="center">
    🧨 An unopinionated Telegram group chat  bot to organize your and your friend's songs 🧨
  </p>
</p>

## Getting started :hatching_chick:

### 1 - Change the bot token on the `docker-compose.yml` file
```
environment:
  - BOT_TOKEN=<paste your token here>
```

### 2 - Install `docker` and build

Run the following commands to boot up the Docker with the proper dependencies installed.
```
$ docker-compose build
$ docker-compose up
```

### 3 - You're ready to go! :tada:

You're sorted! Give the bot a go and interact with it on Telegram to see how he responds! 
You can find the bot on Telegram with the nickname `@banger_music_bot`. 
Make sure to say `/start` at the beginning!
Do not forget though, you need to setup your Google Drive account to make use of this bot! 
Head over to the next section to check how to do this! :smile:

## Setting up your Google Drive account to store your music :musical_note:

> :warning: This is to test the bot for yourself and for development purposes. This will change in the future as we want to keep this bot as safe as possible.

We're planning to host the bot somewhere. However, we are moving the responsibility of storing the files to the users. 
Therefore, you need a Google Drive account for the files to be stored. For this, do the following:

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

* Add `http://localhost:8080` to **Authorized JavaScript origins**.

* Add `http://localhost:8080/` to **Authorized redirect URIs**.

> These URIs will likely change after the bot is hosted. This README will be updated accordingly.

Save your changes and you should be sorted! Give yourself a pat on the back :tada:

### 5 - Download the `.json` credential file
Download your credential `.json` file and paste it in the `src` directory and change its name to `client_secrets.json`.
When you run the bot for the first time, it will prompt you to login the e-mail associated with your Google Drive and it will create a `token.json` file to be used on recurrent sessions.

## Contributing

We're using  [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library as the backbone of this project so check their docs to see how it works.


## License
![License: MIT](https://shields.io/badge/license-MIT-green)


This project is licensed under the MIT License.
