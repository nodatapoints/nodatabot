#!/usr/bin/python3.7

# geklaut vom tutorial

from telegram.ext import Updater, CommandHandler


def hello(bot, update):
    update.message.reply_text('Beep boop I am a robot! Hello {update.message.from_user.first_name}')

with open('token.txt', 'r') as fobj:
	token = fobj.read()

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()