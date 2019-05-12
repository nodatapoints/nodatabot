from basebert import BaseBert, Herberror
from common.chatformat import mono, italic, bold, link_to, ensure_markup_clean
from common.constants import GITHUB_REF, SEP_LINE, HERBERT_TITLE
from common.herbert_utils import getmethods, isownmethod
from decorators import command, aliases
import core
import inspect
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
        {link_to("http://www.python-telegram-bot.org", name="python-telegram-bot")} framework.
        
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


def _format_aliases(alias_list):
    if len(alias_list) == 0:
        return ' '
    res = ' (' + alias_list[0]
    for i in alias_list[1:]:
        res += ', ' + i
    return res + ') '


# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert: BaseBert):
    check_for_(bert.__class__.__name__)

    def providesHelp(member):
        _, method = member # first arg is member name, not needed here
        return hasattr(method, 'command_handler') and method.register_help

    # TODO add unified flag and is_command_handler method to avoid spaghetti
    help_fns = [ *filter(providesHelp, getmethods(bert)) ]

    if len(help_fns) == 0:
        return ''

    res = f"{bold(bert.__class__.__name__)}:\n"
    for _, method in help_fns:
        # if we just inherited this method, dont list it again for this class
        if not isownmethod(method, bert):
            continue

        name, *cmd_aliases = method.commands
        ensure_markup_clean(*method.commands)
        res += f"/{name}" + _format_aliases(cmd_aliases) # TODO somehow figure out args
        if method.__doc__:
            parts = method.__doc__.split(DBLNEWLINE, maxsplit=1)
            ensure_markup_clean(parts[0], msg="The short description of a function can not contain md")
            if len(parts) > 0:
                res += f"- {italic(parts[0].replace(SPACES, ' ').strip())}\n"
            if len(parts) > 1:
                detailed_help_body = helpify_docstring(parts[1])
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
SubBerts he gives you easy access to
can and will offer help to you.
You just have to ask them by their name:

> Use {mono('/help <cmd name>')} for additional information (if available)

"""

HELP_FOOTER = f"""{SEP_LINE}
report bugs and view source on {GITHUB_REF}"""
