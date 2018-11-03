import logging
from functools import wraps


logging.basicConfig(
    style='{',
    format='{asctime} [{levelname:5}] {message}',
    level=logging.INFO
)

class Herberror(Exception):
    '''Basic herbert error'''


def bot_proxy(handler):
    @wraps(handler)
    def wrapper(bot, update, *args, **kwargs):
        try:
            handler(bot, update, *args, **kwargs)

        except (Herberror, AssertionError) as error:
            bot.send_message(update.message.chat_id, *error.args)

        except Exception as e:
            bot.send_message(
                (update.message or update.callback_query.message).chat_id,
                'Oops, something went wrong! :P'
            )
            raise e

    return wrapper


