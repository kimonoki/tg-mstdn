# Introduction
This script creates a telegram bot that can send toot to a given mastodon instance via access token.

## Get token for you bot
Get the token for your telegram bot from @BotFather.

## Run the script


```
python3 tg-mastodon.py $telegram_TOKEN
```
### Run in admin mode to limit user access
```
python3 tg-mastodon.py --admin $telegram_userid $telegram_TOKEN
```

On server, you can run the script from a process management tool like pm2
```
pm2 start 'python3 tg-mastodon.py $telegram_TOKEN'
```

## Use the telegram bot
1. Set mastodon's instance and access token

Go to Preference/Development/New Applications to create a new application and get access token.
Needed access scope is: `read:accounts write:media write:statuses`

```
/set_instance url
/set_accesstoken accesstoken
```

2. Toot

Toot directly from your telegram bot!

Set private or unlisted visibility (default is public) by the command:
```
/set_visibility visibility 
```


## Develop
1. Clone the project. 
2. In python 3 environment. 
Install [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and [Mastodon.py](https://github.com/halcy/Mastodon.py) package


## TODO
- [x] Admin mode
- [ ] Test
- [x] Send toot in different status
- [ ] Send toots in other formats (video etc.)
- [ ] Multiple instances
- [ ] Stream


## try (to deploy)
- Heroku
- VPS
- Online python IDE
