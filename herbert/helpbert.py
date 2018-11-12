from decorators import command, aliases
from basebert import BaseBert
import inspect
import core


__all__ = ['HelpBert']

helpstr = None


class HelpBert(BaseBert):
    @aliases('h')
    @command(pass_args=False)
    def help(self):
        """
        Return a formatted list of all available commands, their arguments and their descriptions.
        """
        self.send_message(helpstr or make_help_str())


def make_help_str():
    global helpstr
    res = HELP_HEADER
    for bert in core.get_berts():
        res += make_bert_str(bert)

    helpstr = res
    return res


# no idea why f"" has problems with those,
# when other single-quoted strings are ok.
NEWLINE = "\n"
DBLNEWLINE = "\n\n"
SPACES = "\s+"


def checkfor_(s):
    assert "_" not in s, "UNTERSTRICHE SIND VERBOTEN!!!!!!"


# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert):
    checkfor_(bert.__class__.__name__)
    res = f"*{bert.__class__.__name__}*:\n"
    for _, method in inspect.getmembers(bert, inspect.ismethod):
        if hasattr(method, 'command_handler'):
            if not method.register_help:
                continue

            name, *cmd_aliases = method.commands
            checkfor_(name + "".join(cmd_aliases))
            res += f"/{name} `<args>` "  # TODO somehow figure out args
            res += f" {tuple(cmd_aliases)} " if cmd_aliases else ""
            if method.__doc__:
                checkfor_(method.__doc__)
                res += f"- _{method.__doc__.split(DBLNEWLINE)[0].replace(SPACES, ' ').strip()}_\n"
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
