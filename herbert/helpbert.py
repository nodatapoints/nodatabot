from decorators import command, aliases, GITHUB_URL
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
            self.send_message(help_str or make_help_str())

        else:
            if help_str is None:
                make_help_str()

            if string in detailed_help:
                self.send_message(detailed_help[string])
            else:
                raise Herberror(f'No further help available for \'{string}\'.')


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


def check_for_(s):
    assert "_" not in s, "UNTERSTRICHE SIND VERBOTEN!!!!!!"


# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert):
    check_for_(bert.__class__.__name__)
    res = f"*{bert.__class__.__name__}*:\n"
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
            check_for_(name + "".join(cmd_aliases))
            res += f"/{name} `<args>` "  # TODO somehow figure out args
            res += f" {tuple(cmd_aliases)} " if cmd_aliases else ""
            if method.__doc__:
                check_for_(method.__doc__)
                parts = method.__doc__.split(DBLNEWLINE, maxsplit=1)
                if len(parts) > 0:
                    res += f"- _{parts[0].replace(SPACES, ' ').strip()}_\n"
                if len(parts) > 1:
                    detailed_help_body = re.sub(ESCAPED_NEWLINE, '',
                                                re.sub(SPACES, ' ', parts[1])
                                                ).strip()
                    detailed_help_str = f"`{name}` (aka `{','.join(cmd_aliases)}`):\n" +\
                                        f"{detailed_help_body}\n"
                    detailed_help[name] = detailed_help_str
                    for alias in cmd_aliases:
                        detailed_help[alias] = detailed_help_str
            else:
                res += "- (documentation is unavailable)\n"

    res += "\n\n"
    res = res.replace(",)", ")").replace("'", "")
    return res


HELP_HEADER = """
```
 _  _         _             _   
| || |___ _ _| |__  ___ _ _| |_ 
| __ / -_) '_| '_ \/ -_) '_|  _|
|_||_\___|_| |_.__/\___|_|  \__|
```
Herbert,
the Herr of the Berts & the Heer of Berts.
for everything you ever want to do,
you just ask Herbert and multiple
Subberts he gives you easy access to
can and will offer help to you.
You just have to ask them by their name:


"""

HELP_FOOTER = """

Use `/help <cmd name>` for additional information (if available)

---
report bugs and view source on [GitHub](""" + GITHUB_URL + ')'
