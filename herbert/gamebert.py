from ast import literal_eval as parse_tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from decorators import command, callback, aliases
from basebert import ImageBaseBert, Herberror
from game import Game
from render import draw_game

names = '👍😂💯'


class GameBert(ImageBaseBert):
    def __init__(self):
        super().__init__()
        self.names = names
        self.available_names = list(self.names)
        self.game = Game(self.names)

        self.users = {}

        self.game_running = False
        self.shown_board_message = None
        self.naming_message = None

    @aliases('show')
    @command(pass_args=False)
    def show_game(self):
        if not self.game_running:
            raise Herberror('Not all players registered yet.')

        if self.shown_board_message is not None:
            self.shown_board_message.delete()

        self.shown_board_message = self.send_photo(
            draw_game(self.game),
            reply_markup=self.game.render_keyboard(
                InlineKeyboardMarkup, InlineKeyboardButton)
        )

    @command(pass_args=False)
    def start(self):
        if self.game_running:
            raise Herberror('Game already running')

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(name, callback_data=name)
             for name in self.available_names]
        ])
        self.naming_message = self.send_message(
            text='Chose your name',
            reply_markup=markup
        )

    def name_handler(self, query):
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
            self.show_game()

    def game_choice_handler(self, query):
        if query.data == 'invalid':
            return

        if self.users[query.from_user] != self.game.expected_player:
            return

        choice = parse_tuple(query.data)
        self.game.push_choice(choice)

        fp = self.pil_image_to_fp(draw_game(self.game), format='PNG')
        self.shown_board_message.edit_media(
            media=InputMediaPhoto(fp),
            reply_markup=self.game.render_keyboard(
                InlineKeyboardMarkup, InlineKeyboardButton)
        )

    @callback(pattern=f'[{names}]')
    def query_handler(self, query):
        if self.game_running:
            self.game_choice_handler(query)

        else:
            self.name_handler(query)
