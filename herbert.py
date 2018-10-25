#!/usr/bin/python3.7

# geklaut vom tutorial

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler

from PIL import Image

def generate_julia(c):
	iterations = 200
	black, white = (0, 0, 0), (255, 255, 255)
	width, height = 500, 500
	scale = 4/max(width, height)

	def iterate(z):
		for i in range(iterations):
			z = z*z + c
			if abs(z) > 2:
				return 3 * (int(i/iterations*255), )

		return white

	image = Image.new('RGB', (width, height))
	for x in range(width):
		for y in range(height):
			color = iterate((x-width/2)*scale + 1j*((y-height/2)*scale))
			image.putpixel((x, y), color)

	image.save('julia.png')

def hello(bot, update):
    update.message.reply_text(f'Beep boop I am a robot! Hello {update.message.from_user.first_name}')

def echo(bot, update):
	update.message.reply_text(f'You said "{update.message.text}"')

def julia(bot, update):
	try:
		_, c_str = update.message.text.split(' ')
		c = complex(c_str)

		generate_julia(c)
		bot.send_photo(chat_id=update.message.chat_id, photo=open('julia.png', 'rb'))

	except ValueError:
		update.message.reply_text(f'Sorry, could not parse "{c_str}"')

buttons = [
    [InlineKeyboardButton("❌", callback_data=1), InlineKeyboardButton(" ", callback_data=1), InlineKeyboardButton("❌", callback_data=1)],
    [InlineKeyboardButton("⭕️", callback_data=1), InlineKeyboardButton(" ", callback_data=1), InlineKeyboardButton("⭕️", callback_data=1)],
    [InlineKeyboardButton("⭕️", callback_data=1), InlineKeyboardButton(" ", callback_data=1), InlineKeyboardButton(" ", callback_data=1)]
]
reply_markup = InlineKeyboardMarkup(buttons, one_time_keyboard=True)

def show_menu(bot, update):
	update.message.reply_text(text="Your move", reply_markup=reply_markup)

with open('token.txt', 'r') as fobj:
	token = fobj.read()

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('echo', echo))
updater.dispatcher.add_handler(CommandHandler('julia', julia))
updater.dispatcher.add_handler(CommandHandler('move', show_menu))

updater.start_polling()
updater.idle()