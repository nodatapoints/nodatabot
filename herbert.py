#!/usr/bin/python3.7

from ast import literal_eval as parse_tuple
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from game import Game
from render import draw_game
from philip import philip_math
from philip import philip_carpet

logging.basicConfig(
	style='{',
	format='{asctime} [{levelname:5}] {message}',
	level=logging.INFO
)

with open('token.txt', 'r') as fobj:
    token = fobj.read()

game = Game('👍😂💯')

shown_board_message = None
markup = game.render_keyboard(InlineKeyboardMarkup, InlineKeyboardButton)

def show_game(bot, update):
    global shown_board_message
    draw_game(game).save('board.png')
    shown_board_message = bot.send_photo(
        update.message.chat_id, open('board.png', 'rb'),
        reply_markup=game.render_keyboard(InlineKeyboardMarkup, InlineKeyboardButton)
    )

def handler(bot, update):
    query = update.callback_query

    if query.data == 'invalid':
        return

    choice = parse_tuple(query.data)
    game.push_choice(choice)

    draw_game(game).save('board.png')
    bot.edit_message_media(
        chat_id=query.message.chat_id,
        message_id=shown_board_message.message_id,
        media=InputMediaPhoto(open('board.png', 'rb')),
        reply_markup=game.render_keyboard(InlineKeyboardMarkup, InlineKeyboardButton)
    )


updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('show', show_game))

# <Philips stuff>
updater.dispatcher.add_handler(CommandHandler('math1', philip_math, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('carpet', philip_carpet, pass_args=True))
# </Philips Stuff>

updater.dispatcher.add_handler(CallbackQueryHandler(handler))

updater.start_polling()
updater.idle()
