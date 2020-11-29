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

You're sorted! Give the bot a go and interact with it on Telegram to see how he responds! You can find the bot on Telegram with the nickname `@banger_music_bot`. Make sure to say `/start` at the beginning!



## Contributing

We're using  [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library as the backbone of this project so check their docs to see how it works.


## License
![License: MIT](https://shields.io/badge/license-MIT-green)


This project is licensed under the MIT License.
