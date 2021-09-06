import time

import raven
import configparser

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

config = configparser.ConfigParser()
config.read_file(open('config.cfg'))
bot_username = config.get("BOT", "bot_username")
support_chat_id = int(config.get("BOT", "support_chat_id"))


def start(update: Update, context: CallbackContext) -> None:
    """ reply on /start message """
    user = update.effective_user
    update.message.reply_text(
        fr'Привет, @{user.username}! Если у тебя возники какие-то трудности при использовании сервиса teasy.one,просто напиши о них в сообщении этому боту :)'
    )


def from_user_message(update: Update, context: CallbackContext) -> None:
    if update.message.text:
        # send message to support
        msg = "{} {}\n{}".format(update.message.chat.id, update.effective_user.mention_markdown(),
                                 update.message.text)
        context.bot.sendMessage(chat_id=support_chat_id, text=msg, parse_mode='Markdown')

    elif update.message.photo:
        msg = "{} {}\n{}".format(update.message.chat.id, update.effective_user.mention_markdown(),
                                 update.message.caption)
        context.bot.sendPhoto(chat_id=support_chat_id, photo=update.message.photo[0].file_id, caption=msg,
                              parse_mode='Markdown')
    elif update.message.document:
        msg = "{} {}\n{}".format(update.message.chat.id, update.effective_user.mention_markdown(),
                                 update.message.caption)
        context.bot.sendDocument(chat_id=support_chat_id, document=update.message.document.file_id, caption=msg,
                                 parse_mode='Markdown')
    elif update.message.video:
        msg = "{} {}\n{}".format(update.message.chat.id, update.effective_user.mention_markdown(),
                                 update.message.caption)
        context.bot.sendVideo(chat_id=support_chat_id, document=update.message.video.file_id, caption=msg,
                              parse_mode='Markdown')


def from_support_message(update: Update, context: CallbackContext) -> None:
    reply_chat_id = None

    # return answer to user
    if update.message.reply_to_message.text:
        reply_chat_id = int(update.message.reply_to_message.text.split(" ")[0])
    elif update.message.reply_to_message.caption:
        reply_chat_id = int(update.message.reply_to_message.caption.split(" ")[0])
    if not reply_chat_id:
        return

    if update.message.text:
        context.bot.sendMessage(chat_id=reply_chat_id, text=update.message.text)
    elif update.message.photo:
        context.bot.sendPhoto(chat_id=reply_chat_id, photo=update.message.photo[0].file_id,
                              caption=update.message.caption, parse_mode='Markdown')
    elif update.message.sticker:
        context.bot.sendSticker(chat_id=reply_chat_id, sticker=update.message.sticker.file_id)
    elif update.message.animation:
        context.bot.sendAnimation(chat_id=reply_chat_id, animation=update.message.animation.file_id)
    elif update.message.document:
        context.bot.sendDocument(chat_id=reply_chat_id, document=update.message.document.file_id)
    elif update.message.video:
        context.bot.sendVideo(chat_id=reply_chat_id, document=update.message.video.file_id,
                              caption=update.message.caption, parse_mode='Markdown')


def message_handler(update: Update, context: CallbackContext) -> None:
    if not update.message or not update.message.chat:
        return
    # check chat type
    if update.message.chat.type == "private" and not update.message.forward_date:
        from_user_message(update, context)
    elif update.message.chat.type == "group" and update.message.chat.id == support_chat_id and update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username:
        from_support_message(update, context)


def main() -> None:
    updater = Updater(config.get("BOT", "token"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    client = raven.Client(
        dsn='https://{}@o989031.ingest.sentry.io/{}'.format(config.get("SENTRY", "pubkey"),
                                                            config.get("SENTRY", "project_id")))
    while True:
        try:
            main()
        except Exception as e:
            client.captureMessage(str(e))
        time.sleep(5)
