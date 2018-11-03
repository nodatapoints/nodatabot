#!/usr/bin/python3.7

from core import *
from decorators import *

from ast import literal_eval as parse_tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from herbert_utils import *
from game import Game
from render import draw_game


class GameBert:
    def __init__(self):
        self.names = '👍😂💯'
        self.available_names = list(self.names)
        self.game = Game(self.names)

        self.users = {}

        self.game_running = False
        self.shown_board_message = None
        self.naming_message = None

    @bot_proxy
    def show_game(self, bot, update):
        if not self.game_running:
            raise Herberror('Not all players registered yet.')

        draw_game(self.game).save('board.png')
        self.shown_board_message = bot.send_photo(
            update.callback_query.message.chat_id, open('board.png', 'rb'),
            reply_markup=self.game.render_keyboard(
                InlineKeyboardMarkup, InlineKeyboardButton)
        )

    @command(pass_args=False)
    def start(self, bot, update):
        if self.game_running:
            raise Herberror('Game already running')

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(name, callback_data=name)
             for name in self.available_names]
        ])
        self.naming_message = bot.send_message(
            update.message.chat_id,
            text='Chose your name',
            reply_markup=markup
        )

    def name_handler(self, bot, update):
        query = update.callback_query
        if query.from_user in self.users:
            return

        self.users[query.from_user] = query.data
        self.available_names.remove(query.data)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(name, callback_data=name)
             for name in self.available_names]
        ])
        user_list_string = '\n'.join(
            f'{name} {user.name}' for user, name in self.users.items())
        self.naming_message.edit_text(
            text=f'Choose your name ({len(self.users)}/{len(self.names)})\n{user_list_string}',
            reply_markup=markup
        )
        if len(self.users) == len(self.names):
            self.naming_message.delete()
            self.game_running = True
            self.show_game(bot, update)

    def game_choice_handler(self, bot, update):
        query = update.callback_query

        if query.data == 'invalid':
            return

        if self.users[query.from_user] != self.game.expected_player:
            return

        choice = parse_tuple(query.data)
        self.game.push_choice(choice)

        draw_game(self.game).save('board.png')
        self.shown_board_message.edit_media(
            media=InputMediaPhoto(open('board.png', 'rb')),
            reply_markup=self.game.render_keyboard(
                InlineKeyboardMarkup, InlineKeyboardButton)
        )

    @callback
    def query_handler(self, *args):
        if self.game_running:
            self.game_choice_handler(*args)

        else:
            self.name_handler(*args)
