"""
Bert

Generates an overview for all avaliable commands
hooks into ../core for this purpose

provided commands:
    - help
"""
import re
from functools import lru_cache
from typing import Dict, List

from basebert import BaseBert
from herberror import Herberror
from common.chatformat import mono, italic, bold, link_to, ensure_markup_clean
from common.constants import GITHUB_REF, SEP_LINE, HERBERT_TITLE
from common.herbert_utils import getmethods, is_own_method, is_cmd_decorated
from decorators import command, aliases, doc
import core
# import inspect


__all__ = ['HelpBert']

detailed_help: Dict[str, str] = dict()


class HelpBert(BaseBert):
    """
    Exposes some commands to view the documentation
    of other command handlers
    """

    @aliases('h')
    @command(pass_string=True)
    @doc("""
        Return a formatted list of all available commands, their arguments and their descriptions.

        Prints a formatted list of available commands.

        An entry looks like m§/<cmd> <params> - <description>§
        Use m§/help <cmd>§ to print more detailed info

        (You already figured that one out if you're reading this text)
        """)
    def help(self, string: str):
        string = string.strip()
        if string == '':
            self.send_message(make_help_str(), disable_web_page_preview=True)

        else:
            # ensure detailed help has been generated
            make_help_str()

            if string in detailed_help:
                self.send_message(detailed_help[string])
            else:
                raise Herberror(f'No further help available for \'{string}\'.')

    @command(pass_args=False)
    @doc(""" Print some meta-information """)
    def about(self):
        self.send_message(helpify_docstring(f"""
        I am a server running an instance of Herbert.
        Herbert is, much to your surprise, a telegram bot.

        It is written in Python and C++, using a custom command dispatcher built on top of the \
        {link_to("http://www.python-telegram-bot.org", name="python-telegram-bot")} framework.

        To find out what it can do, use /help
        To find out how it works, check out the code on {GITHUB_REF}
        """))


@lru_cache(maxsize=1)
def make_help_str():
    res = HELP_HEADER
    for bert in core.berts:
        res += make_bert_str(bert)
    res += HELP_FOOTER

    return res


# no idea why f"" has problems with those,
# when other single-quoted strings are ok.
NEWLINE = '\n'
DBLNEWLINE = '\n\n'
SPACES = r'[\t ]+'
ESCAPED_NEWLINE = r'\\\n'


def _check_for_(string: str):
    assert "_" not in string, "UNTERSTRICHE SIND VERBOTEN!!!!!!"
    assert string.count('`') % 2 == 0, "Balance your backticks!"


def _format_aliases(alias_list: List[str]):
    if len(alias_list) == 0:
        return ' '
    res = ' (' + alias_list[0]
    for i in alias_list[1:]:
        res += ', ' + i
    return res + ') '


def helpify_docstring(string: str):
    """ cleanup spaces so that the given (indented multiline) string looks correct """
    rm_multiple_spaces = re.sub(SPACES, ' ', string)
    return re.sub(ESCAPED_NEWLINE, '', rm_multiple_spaces).strip()


# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert: BaseBert):
    """
    Generate the formatted message part for help on the given bert
    """
    _check_for_(bert.__class__.__name__)

    def provides_help(member):
        """ returns true if the given member function is a command with a nonempty help string """
        _, method = member  # first arg is member name, not needed here
        return is_cmd_decorated(method) and method.cmdinfo.properties.register_help
    help_fns = [*filter(provides_help, getmethods(bert))]

    if len(help_fns) == 0:
        return ''

    res = f"{bold(bert.__class__.__name__)}:\n"
    for _, method in help_fns:
        # if we just inherited this method, dont list it again for this class
        if not is_own_method(method, bert):
            continue

        inf = method.cmdinfo.properties

        name, *cmd_aliases = inf.aliases
        ensure_markup_clean(''.join(inf.aliases))
        # TODO somehow figure out args
        res += f"/{name}" + _format_aliases(cmd_aliases)

        if inf.help_summary != '':
            ensure_markup_clean(inf.help_summary, msg="The short description of a function can not contain md")
            res += f"- {italic(inf.help_summary.replace(SPACES, ' ').strip())}\n"
            if inf.help_detailed != '':
                detailed_help_body = helpify_docstring(inf.help_detailed)
                detailed_help_str = f"{mono(name)} " +\
                                    (f"(aka {mono(','.join(cmd_aliases))}):\n"
                                     if len(cmd_aliases) > 0 else ':\n') + \
                                    f"{detailed_help_body}\n"
                detailed_help[name] = detailed_help_str
                for alias in cmd_aliases:
                    detailed_help[alias] = detailed_help_str
        else:
            res += "- (documentation is unavailable)\n"

    res += "\n\n"
    # res = res.replace(",)", ")").replace("'", "")
    return res


HELP_HEADER = f"""
{HERBERT_TITLE}
Herbert,
the Herr of the Berts & the Heer of Berts.
for everything you ever want to do,
you just ask Herbert and multiple
SubBerts he gives you easy access to
can and will offer help to you.
You just have to ask them by their name:

> Use {mono('/help <cmd name>')} for additional information (if available)

"""

HELP_FOOTER = f"""{SEP_LINE}
report bugs and view source on {GITHUB_REF}"""
