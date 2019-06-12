from decorators import command, doc
from basebert import BaseBert
from herberror import Herberror
from common.chatformat import STYLE_MD


class StackBert(BaseBert):
    def __init__(self):
        self._stack = []

    @command(pass_string=True)
    @doc(""" Pushes given topic on conversation stack """)
    def push(self, topic):
        if not topic:
            raise Herberror('No topic given.')

        if '\n' in topic or len(topic) > 20:
            raise Herberror('One line. 20 Chars.')

        self._stack.append(topic)
        self.send_message(f'Pushed `{topic:.15}` on the stack.', parse_mode=STYLE_MD)

    @command(pass_args=False)
    @doc(""" Displays current conversation stack """)
    def stack(self):
        if not self._stack:
            self.send_message('🗑')
            return

        msg = 'Current conversation stack:\n'
        for i, topic in enumerate(reversed(self._stack)):
            msg += f'`{i:2d} {topic}`\n'

        self.send_message(msg, parse_mode=STYLE_MD)

    @command(pass_args=False)
    @doc(""" Removes top element of the stack, and displays the next topic below """)
    def pop(self):
        if not self._stack:
            raise Herberror('Stack is empty.')

        old_topic = self._stack.pop()
        if not self._stack:
            self.send_message('All done. 👍 The stack is now empty.')

        else:
            self.send_message(f'Popped `{old_topic}`\nNext up: `{self._stack[-1]}`', parse_mode=STYLE_MD)
