import logging
from functools import wraps

__all__ = ['token', 'Herberror', 'bot_proxy', 'logging']

with open('token.txt', 'r') as fobj:
    token = fobj.read()

logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

class Herberror(Exception):
    '''Basic herbert error'''

def bot_proxy(handler):
    @wraps(handler)
    def wrapper(bot, update):
        try:
            generator = handler(bot, update)
            if generator is None:
                return

            for message in generator:
                bot.send_message(update.message.chat_id, message)

        except Herberror as error:
            bot.send_message(update.message.chat_id, *error.args)

    return wrapper