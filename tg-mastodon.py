from mastodon import Mastodon
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
import os
import sys

TOKEN = 'telegram bot token'


# welcome string
def start(update, context):
    bot_send_message(
        update, context, "Hello! You can use this bot to send toots! Type /help for more information")


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def my_info(update, context):
    user_id = update.effective_user.id
    if user_id in accounts_information and all(
            k in accounts_information[user_id] for k in ("instances address", "access token")):
        verify_account(update, context, user_id)
    else:
        notify_incomplete_information(update, context)


# check telegram user id
def send_user_id(update, context):
    user_id = update.effective_user.id
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Your telegram id: {}".format(user_id))


def set_instance_address(update, context):

    if context.args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["instances address"] = context.args[0]
        if "access token" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            verify_account(update, context, user_id)
        else:
            bot_send_message(
                update, context, 'Now please set your access token')


def set_access_token(update, context):

    if context.args:
        user_id = update.effective_user.id
        if user_id not in accounts_information:
            accounts_information[user_id] = {}
        accounts_information[user_id]["access token"] = context.args[0]
        if "instances address" in accounts_information[user_id]:
            set_mastodon_client(user_id)
            verify_account(update, context, user_id)
        else:
            bot_send_message(
                update, context, 'Now please set your instance url')


# send toot to your instance
def toot(update, context, visibility='public'):

    user_id = update.effective_user.id
    if user_exists(user_id) and user_information_is_complete(user_id):
        mastodon_client = accounts_information[user_id]["mastodon client"]
        if update.message.photo:  # for images, save locally and upload to mastodon
            file_path = BASE_FILE_PATH.format(
                update.message.chat_id, update.message.message_id)
            if update.message.caption:
                media_id = upload_media(
                    update, mastodon_client, file_path)
                if not mastodon_client.status_post(update.message.caption, visibility=visibility,
                                                   media_ids=media_id).id:
                    notify_toot_error(update, context)
                else:
                    notify_toot_success(update, context)
            else:
                media_id = upload_media(
                    update, mastodon_client, file_path)
                if not mastodon_client.status_post(status="", visibility=visibility, media_ids=media_id).id:
                    notify_toot_error(update, context)
                else:
                    notify_toot_success(update, context)
            os.remove(file_path)
        else:  # for texts
            toot_text = update.message.text
            if not mastodon_client.status_post(toot_text, visibility=visibility).id:
                notify_toot_error(update, context)
            else:
                notify_toot_success(update, context)
    else:
        notify_incomplete_information(update, context)


# helper functions
def verify_account(update, context, user_id):
    try:
        mastodon_client = accounts_information[user_id]["mastodon client"]
        mastodon_client.account_verify_credentials()
    except Exception:
        # token or instance not correct
        bot_send_message(
            update, context, "Your information seems to be incorrect. Please reset your instance url and access token")
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Done! Your can now toot as {} to {}".format(
                mastodon_client.account_verify_credentials()["display_name"] or mastodon_client.account_verify_credentials()["username"],
                accounts_information[user_id]["instances address"]), disable_web_page_preview=True)


def create_media_dir():
    if not os.path.exists(os.path.dirname(sys.argv[0]) + '/tmp'):
        os.makedirs(os.path.dirname(sys.argv[0]) + '/tmp')


def set_mastodon_client(user_id):
    accounts_information[user_id]["mastodon client"] = Mastodon(
        access_token=accounts_information[user_id]["access token"],
        api_base_url=accounts_information[user_id]["instances address"]
    )


def upload_media(update, mastodon_client, file_path):

    new_file = update.message.photo[-1].get_file()
    new_file.download(file_path)
    media_id = mastodon_client.media_post(file_path, description=" ").id
    return media_id


def notify_incomplete_information(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='You have not set your mastodon account yet!')


def bot_send_message(update, context, message):

    context.bot.send_message(chat_id=update.message.chat_id, text=message)


def notify_toot_success(update, context):
    bot_send_message(update, context, 'Tooted!')


def notify_toot_error(update, context):
    bot_send_message(update, context, 'Error! Sending toot failed!')


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
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

accounts_information = {}

# main help message in markdown format
help_message = """\
Use /set\_instance and /set\_accesstoken to set your account.
Use /myinfo to check if your mastodon account is correctly set up

Send your toots (texts, images) *directly* to me(without command) when you are set up
Generate your `access` token in Preference->Development with `read and write permission`
Format of the instance url should be: https://octodon.social

You can check out the source code on github
"""

BASE_FILE_PATH = os.path.abspath(
    os.path.dirname(sys.argv[0])) + '/tmp/{}_{}.png'

# start and help handler
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help)
myinfo_handler = CommandHandler('myinfo', my_info)

# commands handlers
userid_handler = CommandHandler('id', send_user_id)
instance_handler = CommandHandler('set_instance', set_instance_address)
access_token_handler = CommandHandler('set_accesstoken', set_access_token)

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
    try:
        create_media_dir()
        updater.start_polling()
    except KeyboardInterrupt:  # kill script manually
        print('Interrupted')
        sys.exit()
