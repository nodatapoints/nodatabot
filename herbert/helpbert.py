from common import chatformat
from decorators import command, aliases
from common.constants import GITHUB_REF, SEP_LINE, HERBERT_TITLE
from basebert import BaseBert, Herberror
import inspect
import core
import re


__all__ = ['HelpBert']

help_str = None
detailed_help = dict()


class HelpBert(BaseBert):
    @aliases('h')
    @command(pass_string=True)
    def help(self, string):
        """
        Return a formatted list of all available commands, their arguments and their descriptions.

        Prints a formatted list of available commands.

        An entry looks like /<cmd> <params> - <description>
        Use /help <cmd> to print more detailed info

        (You already figured that one out if you're reading this text)
        """
        string = string.strip()
        if string == '':
            self.send_message(help_str or make_help_str(), disable_web_page_preview=True)

        else:
            if help_str is None:
                make_help_str()

            if string in detailed_help:
                self.send_message(detailed_help[string])
            else:
                raise Herberror(f'No further help available for \'{string}\'.')

    @command(pass_args=False)
    def about(self):
        """Print some meta-information"""
        self.send_message(helpify_docstring(f"""
        I am a server running an instance of Herbert.
        Herbert is, much to your surprise, a telegram bot.
        
        It is written in Python and C++, using a custom command dispatcher built on top of the \
        {chatformat.link_to("http://www.python-telegram-bot.org", name="python-telegram-bot")} framework.
        
        To find out what it can do, use /help
        To find out how it works, check out the code on {GITHUB_REF}
        """))


def make_help_str():
    global help_str
    res = HELP_HEADER
    for bert in core.berts:
        res += make_bert_str(bert)
    res += HELP_FOOTER

    help_str = res
    return res


# no idea why f"" has problems with those,
# when other single-quoted strings are ok.
NEWLINE = '\n'
DBLNEWLINE = '\n\n'
SPACES = r'[\t ]+'
ESCAPED_NEWLINE = r'\\\n'


def check_for_(s: str):
    assert "_" not in s, "UNTERSTRICHE SIND VERBOTEN!!!!!!"
    assert s.count('`') % 2 == 0, "Balance your backticks!"


# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert: BaseBert):
    check_for_(bert.__class__.__name__)
    res = f"{chatformat.bold(bert.__class__.__name__)}:\n"
    for _, method in inspect.getmembers(bert, inspect.ismethod):
        # if we just inherited this method, dont list it again for this class
        is_own_fn = True
        for baseclass in bert.__class__.__bases__:
            if hasattr(baseclass, method.__name__):
                is_own_fn = False
                break

        if not is_own_fn:
            continue

        if hasattr(method, 'command_handler'):  # TODO add unified flag and is_command_handler method to avoid spaghetti
            if not method.register_help:
                continue

            name, *cmd_aliases = method.commands
            chatformat.ensure_markup_clean(name + "".join(cmd_aliases))
            res += f"/{name} {chatformat.mono('<args>', escape=True)} "  # TODO somehow figure out args
            res += f" {tuple(cmd_aliases)} " if cmd_aliases else ""
            if method.__doc__:
                parts = method.__doc__.split(DBLNEWLINE, maxsplit=1)
                chatformat.ensure_markup_clean(parts[0], msg="The short description of a function can not contain md")
                if len(parts) > 0:
                    res += f"- {chatformat.italic(parts[0].replace(SPACES, ' ').strip())}\n"
                if len(parts) > 1:
                    detailed_help_body = helpify_docstring(parts[1])
                    detailed_help_str = f"{chatformat.mono(name)} " +\
                                        (f"(aka {chatformat.mono(','.join(cmd_aliases))}):\n"
                                            if len(cmd_aliases) > 0 else ':\n') + \
                                        f"{detailed_help_body}\n"
                    detailed_help[name] = detailed_help_str
                    for alias in cmd_aliases:
                        detailed_help[alias] = detailed_help_str
            else:
                res += "- (documentation is unavailable)\n"

    res += "\n\n"
    res = res.replace(",)", ")").replace("'", "")
    return res


def helpify_docstring(s):
    return re.sub(ESCAPED_NEWLINE, '', re.sub(SPACES, ' ', s)).strip()


HELP_HEADER = f"""
{HERBERT_TITLE}
Herbert,
the Herr of the Berts & the Heer of Berts.
for everything you ever want to do,
you just ask Herbert and multiple
Subberts he gives you easy access to
can and will offer help to you.
You just have to ask them by their name:

&gt; Use {chatformat.mono('/help <cmd name>', escape=True)} for additional information (if available)

"""

HELP_FOOTER = f"""{SEP_LINE}
report bugs and view source on {GITHUB_REF}"""
