# Introduction
This script creates a telegram bot that can send toot to a given mastodon instance via access token.


## Use the bot
1. Set the token for telegram bot. [link](https://github.com/kimonoki/tg-mstdn/blob/33eefe4b9122e90b4a48ef5b69a1bcb4a5eb554f/octondonbot.py#L8)
2. Set mastodon's instance and access token
3. Toot

### Toot with images
Just send the image to the bot. Add caption if you want to send texts with the image.


## Develop
1. Clone the project. 
2. In python 3 environment. 
Install [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and [Mastodon.py](https://github.com/halcy/Mastodon.py) package

### API used
This bot uses python-telegram package and Mastodon.py with telegram and Mastodon API. (support the latest version 2021-09-24)


## TODO
- Test
- Error Handling
- Send toot in different status
- Send toots in other formats (video etc.)
- Multiple instances
- Stream


## try (to deploy)
- Heroku
- VPS
- Online python IDE
