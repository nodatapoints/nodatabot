import logging
from functools import wraps
from hercurles_chat import _t_reply_err


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


def handle_herberrors(fn):
    @wraps(fn)
    def wrapper(self, bot, update, *args, **kwargs):
        up = update if update.message else update.callback_query
        try:
            return fn(self, bot, update, *args, **kwargs)
        except (AssertionError, Herberror) as e:
            _t_reply_err(bot, up, str(e))
        except Exception:
            _t_reply_err(bot, up, "Something broke. I'll fix it later, try doing something nicer first.")
            raise

    return wrapper

