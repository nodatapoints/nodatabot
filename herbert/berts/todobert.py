from common import chatformat
from common.chatformat import STYLE_MD
from decorators import command, aliases
from basebert import BaseBert, Herberror, BadHerberror

from pathlib import Path
todo_file = Path('todo.txt')

MARKDOWNEXTRA = 2
MAXLENGTHKEY = 6
COLON = ': '


class TodoBert(BaseBert):
    @aliases('td')
    @command(pass_args=False)
    def todo(self):
        """
        Return a list of open requests

        The whole TodoBert has been built to keep track of all the things\
        that we still need to implement. It keeps them in a list, which can be expanded by\
        everyone finding something which still needs to be done. This command is used to display all the requests\
        in a formated list with markdwn for better recognizablity

        e.g: `/td`
        """
        try:
            with todo_file.open() as fobj:
                self.send_message('`        Stuff to do:`\n' +
                                  fobj.read(), parse_mode=STYLE_MD)
        except Exception:
            raise BadHerberror('todo.txt not found')

    @aliases('+todo', 'td+')
    @command
    def addtodo(self, args):
        """
        Add an request to the list

        See `/help todo` for the concept of the todo utility.
        This command is used to append new requests and ideas to the end of the list. Use the first \
        (<= 6 characters long) word as a key or heading to your request and the following ones to describe\
        what you want

        e.g: `/td+ $$$ I want Ca$h`
        """
        try:
            todo_file.open('r+')  # to catch not found
            with todo_file.open('a') as fobj:
                key = f'{args[0]:>{MAXLENGTHKEY}.{MAXLENGTHKEY}}'
                door = ' '.join(args[1:])  # wohoo format strings
                if '_' in key or '_' in door or '*' in key or '*' in door:
                    raise Herberror(
                        'Markup Characters cause Fuckups, please use alternatives')

                fobj.write(
                    f'`{key}{COLON}`{chatformat.italic(door, style=chatformat.STYLE_MD)}\n')
                self.send_message(f'Your request was added to the list.')
        except Exception:
            raise BadHerberror('todo.txt not found')

    @aliases('-todo', 'td-')
    @command
    def removetodo(self, args):
        """
        Remove a request from the list

        See `/help todo` for the concept of the todo utility.
        This command is used to remove requests from the list. Use the key that specifies the request\
        to address and remove it. All requests with that key will get removed.

        e.g: '/td- $$$`
        """
        try:
            with todo_file.open('r+') as fobj:
                lines = fobj.readlines()
                fobj.seek(0)
                edited = False
                for element in lines:
                    if findkey_td(args[0], element):
                        element = f'`{args[0]}{COLON}`{element[MARKDOWNEXTRA+MAXLENGTHKEY+len(COLON):].rstrip()}'
                        self.send_message(
                            f'Thank you for finishing: \n"{element}"', parse_mode=STYLE_MD)
                        edited = True
                    else:
                        fobj.write(element)
                fobj.truncate()
                if not edited:
                    self.send_message(
                        f'Your query did not match any requests.')
        except Exception:
            raise BadHerberror('todo.txt not found')

    @aliases('%todo', 'td%')
    @command
    def edittodo(self, args):
        """
        Edit a request in the list

        See `/help todo` for the concept of the todo utility.
        This command is used to edit requests in the list. Use the the first word as the key that specifies\
        the request and the following words to rewrite the content of that request.

        e.g: '/td% $$$ maybe there are more important things in life`
        """
        try:
            with todo_file.open('r+') as fobj:
                lines = fobj.readlines()
                fobj.seek(0)
                edited = False
                for element in lines:
                    if findkey_td(args[0], element):
                        door = ' '.join(args[1:])  # markdown!
                        if '_' in door or '*' in door:
                            raise Herberror(
                                'Markup Characters cause Fuckups, please use alternatives')
                        fobj.write(
                            f'{element[:MARKDOWNEXTRA+MAXLENGTHKEY+len(COLON)]}{chatformat.italic(door, style=chatformat.STYLE_MD)}\n')
                        self.send_message(f'You successfully edited the list.')
                        edited = True
                    else:
                        fobj.write(element)
                fobj.truncate()
                if not edited:
                    self.send_message(
                        f'Your query did not match any requests.')
        except Exception:
            raise BadHerberror('todo.txt not found')


def findkey_td(key, string):
    length = MAXLENGTHKEY + len(COLON)
    full_key = f'`{(key+COLON):>{length}.{length}}`'

    if full_key == string[:length + MARKDOWNEXTRA]:  # markdown ``, fix if depecated
        return True
    return False
