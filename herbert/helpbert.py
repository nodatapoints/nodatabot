from decorators import command, aliases
from basebert import BaseBert, Herberror
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

    @aliases('td')
    @command
    def todo(self, args):
        """
        Return a formatted list of all the open requests
        """
        file = open('todo.txt', 'r')
        output = "" 
        for element in file: # TODO better python way   
            output += element
        self.send_message(output)
        file.close()

    @aliases('+todo', 'td+')
    @command
    def addtodo(self, args):
        """
        Add an additional keyspecified element to the open requests 
        """
        file = open('todo.txt', 'a')
        key = '{:>6.6}'.format(args[0])
        door = ' '.join(args[1:]) # wohoo format strings
        if '_' in key or '_' in door or '*' in key or '*' in door:
            raise Herberror('Markup Characters cause Fuckups, please use alternatives')
        file.write(f'`{key}: `_{door}_\n')
        file.close();
        self.send_message(f'Your request was added to the list.')

    @aliases('-todo', 'td-')
    @command
    def removetodo(self, args):
        """
        Remove the keyspecified element from the open requests
        """
        file = open('todo.txt', 'r')
        lines = file.readlines()
        file.close()
        file = open('todo.txt', 'w')
        for element in lines:
            if element[:10].find(args[0]+": `") == -1:
                file.write(element)
            else:
                self.send_message(f'Thank you for finishing:\n"{element[:-1]}"')

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
        if hasattr(method, '_command_handler'):
            if not method._register_help:
                continue

            name, *aliases = method._commands
            checkfor_(name + "".join(aliases))
            res += f"/{name} `<args>` "  # TODO somehow figure out args
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
Herbert,
the Herr of the Berts & the Heer of Berts.
for everything you ever want to do,
you just ask Herbert and multiple
Subberts he gives you easy access to
can and will offer help to you.
You just have to ask them by their name:


"""
