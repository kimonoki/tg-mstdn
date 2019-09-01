from mastodon import Mastodon
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
import os
import sys

TOKEN = 'your telegram bot TOKEN'


# welcome string
def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello! You can use this bot to send toots! Type /help for more information")


def help(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=help_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def my_info(bot, update):
    user_id = update.effective_user.id
    if user_id in accounts_information and all(
            k in accounts_information[user_id] for k in ("instances address", "access token")):
        verify_account(bot, update, user_id)
    else:
        notify_incomplete_information(bot, update)


# check telegram user id
def send_user_id(bot, update):
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text="Your telegram id: {}".format(user_id))


def set_instance_address(bot, update, args):
    if args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["instances address"] = args[0]
        if "access token" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            verify_account(bot, update, user_id)
        else:
            notify_missing_information(bot, update, 'Now please set your access token')


def set_access_token(bot, update, args):
    if args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["access token"] = args[0]
        if "instances address" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            verify_account(bot, update, user_id)
        else:
            notify_missing_information(bot, update, 'Now please set your instance url')


# send toot to your instance
def toot(bot, update, visibility='public'):
    user_id = update.effective_user.id
    if user_exists(user_id) and user_information_is_complete(user_id):
        mastodon_client = accounts_information[user_id]["mastodon client"]
        if update.message.photo:  # for images, save locally and upload to mastodon
            file_path = BASE_FILE_PATH.format(update.message.chat_id, update.message.message_id)
            if update.message.caption:
                media_id = upload_media(bot, update, mastodon_client, file_path)
                if not mastodon_client.status_post(update.message.caption, visibility=visibility,
                                                   media_ids=media_id).id:
                    notify_toot_error(bot, update)
                else:
                    notify_toot_success(bot, update)
            else:
                media_id = upload_media(bot, update, mastodon_client, file_path)
                if not mastodon_client.status_post(status="", visibility=visibility, media_ids=media_id).id:
                    notify_toot_error(bot, update)
                else:
                    notify_toot_success(bot, update)
            os.remove(file_path)
        else:  # for texts
            toot_text = update.message.text
            if not mastodon_client.status_post(toot_text, visibility=visibility).id:
                notify_toot_error(bot, update)
            else:
                notify_toot_success(bot, update)
    else:
        notify_incomplete_information(bot, update)


# helper functions
def verify_account(bot, update, user_id):
    try:
        mastodon_client = accounts_information[user_id]["mastodon client"]
        mastodon_client.account_verify_credentials()
    except Exception:
        # token or instance not correct
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Your information seems to be incorrect. Please reset your instance url and access token")
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Done! Your can now toot as {} to {}".format(
                mastodon_client.account_verify_credentials()["display_name"],
                accounts_information[user_id]["instances address"]), disable_web_page_preview=True)


def create_media_dir():
    if not os.path.exists(os.path.dirname(sys.argv[0]) + '/tmp'):
        os.makedirs(os.path.dirname(sys.argv[0]) + '/tmp')


def set_mastodon_client(user_id):
    accounts_information[user_id]["mastodon client"] = Mastodon(
        access_token=accounts_information[user_id]["access token"],
        api_base_url=accounts_information[user_id]["instances address"]
    )


def upload_media(bot, update, mastodon_client, file_path):
    new_file = update.message.photo[-1].get_file()
    new_file.download(file_path)
    media_id = mastodon_client.media_post(file_path, description="test").id
    return media_id


def notify_incomplete_information(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='You have not set your mastodon account yet!')


def notify_missing_information(bot, update, information):
    bot.send_message(chat_id=update.message.chat_id, text=information)


def notify_toot_success(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Tooted!')


def notify_toot_error(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Error! Sending toot failed!')


def user_exists(user_id):
    if user_id in accounts_information:
        return True
    else:
        return False


def user_information_is_complete(user_id):
    if "mastodon client" in accounts_information[user_id] and "instances address" in \
            accounts_information[user_id]:
        return True
    else:
        return False


# telegram API TOKEN
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

accounts_information = {}

# main help mesage in markdown format
help_message = """\
Use /set\_instance and /set\_accesstoken to set your account.
Use /myinfo to check if your mastodon account is correctly set up

Send your toots (texts, images) *directly* to me(without command) when you are set up
Generate your `access` token in Preference->Development with `read and write permission`
Format of the instance url should be: https://octodon.social

You can check out the source code on github
"""

BASE_FILE_PATH = os.path.abspath(os.path.dirname(sys.argv[0])) + '/tmp/{}_{}.png'

# start and help handler
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
myinfo_handler = CommandHandler('myinfo', my_info)

# commands handlers
userid_handler = CommandHandler('id', send_user_id)
instance_handler = CommandHandler('set_instance', set_instance_address, pass_args=True)
access_token_handler = CommandHandler('set_accesstoken', set_access_token, pass_args=True)

toot_handler = MessageHandler(filters=Filters.text | Filters.photo, callback=toot)

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
    create_media_dir()
    updater.start_polling()
