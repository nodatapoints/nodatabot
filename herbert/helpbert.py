from decorators import command
from basebert import BaseBert
import inspect
import core

__all__ = ['HelpBert']

helpstr = None


class HelpBert(BaseBert):
    @command(pass_args=False)
    def help(self):
        """
        Return a formatted list of all available commands, their arguments and their descriptions.
        """
        self.send_message(helpstr or make_help_str())


def make_help_str():
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
    assert not "_" in s, "UNTERSTRICHE SIND VERBOTEN!!!!!!"

    
# this is bodgy, please fix (but without destroying it).
def make_bert_str(bert):
    checkfor_(bert.__class__.__name__)
    res = f"*{bert.__class__.__name__}*:\n"
    for _, method in inspect.getmembers(bert, inspect.ismethod):
        if hasattr(method, '_command_handler'):
            name, *aliases = method._commands
            checkfor_(name + "".join(aliases))
            res += f"/{name} `<args>` " # TODO somehow figure out args
            res += f" {tuple(aliases)} " if aliases else "" 
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
This is the one and only Bert.
But i cant be bothered to write
a full description right now.

# TODO


"""

