"""
Module that contains the Herbot Prefix Handler
"""

from telegram import Update
from telegram.ext import CommandHandler


class HerbotPrefixHandler(CommandHandler):
    """
    This class is basically equivalent to a telegram.ext.PrefixHandler,
    but also accepts commands of the form /command@botname
    """

    def __init__(self, command, callback, **kwargs):
        self._command_list = [command] if isinstance(command, str) else list(command)

        super().__init__(
            'nocommand',
            callback,
            **kwargs
        )

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message is not None:
            message = update.effective_message

            bot_name = message.bot.username if message.bot else None

            if message.text:
                command, *args = message.text.split()
                command_tag = command[0]
                command_name = command[1:]

                if command_tag != '/':
                    return False

                parts = command_name.split('@')

                if len(parts) > 2:
                    return False

                if bot_name and len(parts) > 1 and parts[1] != bot_name:
                    return False

                if parts[0] not in self._command_list:
                    return False

                return args, True

        return None

    def collect_additional_context(self, context, update, dispatcher, check_result):
        if isinstance(check_result, tuple):
            context.args = check_result[0]
            if isinstance(check_result[1], dict):
                context.update(check_result[1])
