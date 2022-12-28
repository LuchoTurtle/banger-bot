# Getting it running

You need to create yourself a Telegram bot. It's super easy, you can follow these [official instructions](https://core.telegram.org/bots#creating-a-new-bot).

After this, you'll  have access to a Bot Token. Now you have two ways of getting the bot running!

> :warning: Do not forget, you need to
setup your Google Drive account for the bot to work.
Check the [Google Drive guide](./drive.md) to get started.
>
> It is important to have the `client_secrets.json` 
and `token.json` files before running docker.
To get these, you will need to run the program locally and
authorize the application (it will open a chrome window).

## Using docker :whale: (much easier!)

##### 1 - Change the bot token on the `docker-compose.yml` file
```
environment:
  - BOT_TOKEN=<paste your token here>
```

##### 2 - Install `docker`, build and get it running

Run the following commands to boot up the Docker with the proper dependencies installed.
```
$ docker-compose build
$ docker-compose up
```

## Vanilla python :snake:

##### 1 - Change bot token on the `.env_example` file.
Type your secret bot token on this file and change it to `.env` so the bot can call it.

```
BOT_TOKEN=<bot token here>
```

##### 2 - Install requirements
Install the needed requirements.
```
pip install -r requirements.txt
```

##### 3 - Install ffmpeg
You need to install [ffmpeg](https://www.ffmpeg.org/) so music can be properly detected.
Install it and add it to your $PATH environment variable.

##### 4 - Add root folder to $PYTHONPATH
In order for the modules to work within the project, you need to add the **root of the project** to $PYTHONPATH.

##### 5 - Run it!
Just run the main python script with
```
python main.py
```


### You're ready to go! :tada:

You're sorted! Give the bot a go and interact with it on Telegram to see how he responds! Make sure to say `/start` at the beginning!
