from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from mastodon import Mastodon


# welcome string
def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello! You can use this bot to send toots! Type /help for more information")


def help(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Use /set_instance and /set_accesstoken to set your account."
             "\nUse /myinfo to check your mastodon account"
             "\n/toot to send a toot in public visibility"
             "\n\nGenerate your access token in Preference->Development"
             "\nFormat of the instance url should be: https://octodon.social")


def my_info(bot, update):
    user_id = update.effective_user.id
    if user_id in accounts_information and all(
            k in accounts_information[user_id] for k in ("instances address", "access token")):
        mastodon_client = accounts_information[user_id]["mastodon client"]
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Your can now toot as %s" % mastodon_client.account_verify_credentials()["display_name"])
    else:
        notify_incomplete_information(bot, update)


# check telegram user id
def send_user_id(bot, update):
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text="Your telegram id: %s" % user_id)


def set_instance_address(bot, update, args):
    if args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["instances address"] = args[0]
        if "access token" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Done! You can now send toot to %s' % accounts_information[user_id][
                                 "instances address"])
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Now please set your access token')


def set_access_token(bot, update, args):
    if args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["access token"] = args[0]
        if "instances address" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            bot.send_message(chat_id=update.message.chat_id,
                             text='Done! You can now send toot to %s' % accounts_information[user_id][
                                 "instances address"])
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Now please set your instance url')


# send toot to octodon
def toot(bot, update, args):
    if args:
        user_id = update.effective_user.id
        if user_id in accounts_information and "mastodon client" in accounts_information[user_id]:
            toot = ' '.join(args)
            mastodon_client = accounts_information[user_id]["mastodon client"]
            mastodon_client.status_post(toot, visibility='unlisted')
            bot.send_message(chat_id=update.message.chat_id, text='toot success')
        else:
            notify_incomplete_information(bot, update)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Empty toot. Sent nothing')


# helper functions
def set_mastodon_client(user_id):
    accounts_information[user_id]["mastodon client"] = Mastodon(
        access_token=accounts_information[user_id]["access token"],
        api_base_url=accounts_information[user_id]["instances address"]
    )


def notify_incomplete_information(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='You have not set your mastodon account yet!')


# telegram API TOKEN
updater = Updater(token='')
dispatcher = updater.dispatcher

accounts_information = {}

# start and help handler
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
myinfo_handler = CommandHandler('myinfo', my_info)

# commands handlers
userid_handler = CommandHandler('id', send_user_id)
instance_handler = CommandHandler('set_instance', set_instance_address, pass_args=True)
access_token_handler = CommandHandler('set_accesstoken', set_access_token, pass_args=True)
toot_handler = CommandHandler('toot', toot, pass_args=True)

# add to dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(myinfo_handler)
dispatcher.add_handler(userid_handler)
dispatcher.add_handler(instance_handler)
dispatcher.add_handler(access_token_handler)
dispatcher.add_handler(toot_handler)

# debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# start the bot
if __name__ == '__main__':
    updater.start_polling()
