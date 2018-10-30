#!/usr/bin/python3.7

from ast import literal_eval as parse_tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from herbert_utils import *
from game import Game
from render import draw_game
from philip import philip_math, philip_carpet

aliases = '👍😂💯'
available_aliases = list(aliases)
game = Game(aliases)

users = {}

game_running = False
shown_board_message = None
alias_message = None

@bot_proxy
def show_game(bot, update):
    global shown_board_message
    if not game_running:
        raise Herberror('Not all players registrated yet.')

    draw_game(game).save('board.png')
    shown_board_message = bot.send_photo(
        update.callback_query.message.chat_id, open('board.png', 'rb'),
        reply_markup=game.render_keyboard(InlineKeyboardMarkup, InlineKeyboardButton)
    )

def show_aliases(bot, update):
    global alias_message
    if game_running:
        raise Herberror('Game already running')

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(alias, callback_data=alias) for alias in available_aliases]
    ])
    alias_message = bot.send_message(
        update.message.chat_id,
        text='Chose your alias',
        reply_markup=markup
    )

def alias_handler(bot, update):
    global game_running

    query = update.callback_query
    if query.from_user in users:
        return

    users[query.from_user] = query.data
    available_aliases.remove(query.data)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(alias, callback_data=alias) for alias in available_aliases]
    ])
    user_list_string = '\n'.join(f'{alias} {user.name}' for user, alias in users.items())
    alias_message.edit_text(
        text=f'Choose your alias ({len(users)}/{len(aliases)})\n{user_list_string}',
        reply_markup=markup
    )
    if len(users) == len(aliases):
        alias_message.delete()
        game_running = True
        show_game(bot, update)

def game_choice_handler(bot, update):
    query = update.callback_query

    if query.data == 'invalid':
        return

    if users[query.from_user] != game.expected_player:
        return

    choice = parse_tuple(query.data)
    game.push_choice(choice)

    draw_game(game).save('board.png')
    bot.edit_message_media(  # TODO use edit_media
        chat_id=query.message.chat_id,
        message_id=shown_board_message.message_id,
        media=InputMediaPhoto(open('board.png', 'rb')),
        reply_markup=game.render_keyboard(InlineKeyboardMarkup, InlineKeyboardButton)
    )

def query_handler(*args):
    if game_running:
        game_choice_handler(*args)

    else:
        alias_handler(*args)

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('show', show_game))
updater.dispatcher.add_handler(CommandHandler('start', show_aliases))

# <Philips stuff>
updater.dispatcher.add_handler(CommandHandler('math1', philip_math, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('carpet', philip_carpet, pass_args=True))
# </Philips Stuff>

updater.dispatcher.add_handler(CallbackQueryHandler(query_handler))

updater.start_polling()
updater.idle()
