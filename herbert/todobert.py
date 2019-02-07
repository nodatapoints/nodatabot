from common import chatformat
from common.chatformat import STYLE_MD
from decorators import command, aliases
from basebert import BaseBert, Herberror

from pathlib import Path

todo_file = Path('todo.txt')


class TodoBert(BaseBert):
    @aliases('td')
    @command(pass_args=False)
    def todo(self):
        """
        Return a formatted list of all the open requests
        """
        with todo_file.open() as fobj:
            self.send_message(fobj.read(), parse_mode=STYLE_MD)

    @aliases('+todo', 'td+')
    @command
    def addtodo(self, args):
        """
        Add an additional keyspecified element to the open requests
        """
        with todo_file.open('a') as fobj:
            key = f'{args[0]:>6.6}'
            door = ' '.join(args[1:])  # wohoo format strings
            if '_' in key or '_' in door or '*' in key or '*' in door:
                raise Herberror('Markup Characters cause Fuckups, please use alternatives')

            fobj.write(f'`{key}: `{chatformat.italic(door, use_style=chatformat.STYLE_MD)}\n')
            self.send_message(f'Your request was added to the list.')

    @aliases('-todo', 'td-')
    @command
    def removetodo(self, args):
        """
        Remove the keyspecified element from the open requests
        """
        with todo_file.open('r+') as fobj:
            lines = fobj.readlines()
            fobj.seek(0)
            for element in lines:
                if args[0] + ': `' in element[:10]:  # TODO @Philip magic numbers...
                    self.send_message(f'Thank you for finishing:\n"{element[:-1]}"', parse_mode=STYLE_MD)
                else:
                    fobj.write(element)

            fobj.truncate()
