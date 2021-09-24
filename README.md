# Introduction
This script creates a telegram bot that can send toot to a given mastodon instance via access token.

## Get token for you bot
Edit the script to set the token for your telegram bot. [link](https://github.com/kimonoki/tg-mstdn/blob/f79cd6b1469eb3696d377e7af24a2f09d6f2e06c/tg-mastodon.py#L8)

## Run the script
On server, you can run from a process management tool like pm2
```
pm2 start tg-mastodon.py --interpreter python3
```

## Use the telegram bot
1. Set mastodon's instance and access token

Needed access scope is: `read:accounts write:media write:statuses`

```
/set_instance url
/set_accesstoken accesstoken
```

2. Toot



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
