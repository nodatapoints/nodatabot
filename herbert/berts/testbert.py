"""
Bert + Tests

Provides some debug commands to create
exceptions and format text

Also provides an entrypoint, which will
run some command handlers and both check
whether they will produce the
correct result and whether the result
is able to be passed through the layers
of decorators up to the calling ptb library
"""
import re
from typing import Callable, Type, List
from datetime import datetime
from dataclasses import dataclass

from common import chatformat
from common.argparser import Args, UnexpectedArgument, ArgumentFormatError
from common.chatformat import render_style_para, STYLE_HTML, mono
from common.basic_utils import require
from basebert import BaseBert
from herberror import Herberror, BadHerberror
from decorators import command, aliases

from berts.asciimath import AsciiBert
from berts.hashbert import HashBert
from berts.helpbert import HelpBert
from berts.interprert import InterpRert
from berts.texbert import TexBert


class TestBert(BaseBert):
    """
    Wraps some debug functions
    """

    @aliases('dbg_e')
    @command(register_help=False, pass_string=True)
    def debug_error(self, string):
        """ create a herberror with the given message """
        require(self)
        raise Herberror(string)

    @aliases('dbg_be')
    @command(register_help=False, pass_string=True)
    def debug_bad_error(self, string: str):
        """ create a fatal herberror with the given message """
        require(self)
        raise BadHerberror(string)

    @aliases('dbg_ue')
    @command(register_help=False, pass_string=True)
    def debug_unexpected_error(self, string: str):
        """ create a non-herberror exception """
        require(self)
        raise ValueError(string)

    @aliases('dbg_md')
    @command(register_help=False, pass_string=True)
    def dbg_print_formatted(self, string: str):
        """ output all markdown variants """
        self.reply_text(chatformat.bold(string) + chatformat.italic(string) + chatformat.mono(string) + string,
                        parse_mode=chatformat.get_parse_mode())

    @aliases('dbg_r')
    @command(register_help=False, pass_string=True)
    def dbg_render_md(self, string: str):
        """ parse backend format escapes """
        self.reply_text(render_style_para(string), caption='abc',
                        parse_mode=chatformat.STYLE_BACKEND)

    @aliases('dbg_mdx')
    @command(register_help=False, pass_args=True)
    def dbg_markdown_xcode(self, args):
        """
        parse the given string with a parse mode specified in
        the first word of the argument
        """
        if len(args) <= 1:
            return
        self.reply_text("".join(args[1:]), parse_mode=args[0])

    @command(register_help=False, pass_string=True)
    def dbg_parse(self, string: str):
        """
        Parse markup tags in the input and return both
        the text as well as a description of the respective
        message entities
        """
        self.reply_text(string, parse_mode=STYLE_HTML)

        _text, entities = chatformat.parse_entities(string, STYLE_HTML)
        self.reply_text('\n'.join(mono(f'E {e.offset} {e.length}') for e in entities))


def test():
    """
    UNIT TESTING

    just run `python3.7 testbert.py`

    there are by no means enough tests to avoid most bugs, but at least this
    should help to catch some mistakes somewhat easier. please add more tests.
    """

    @dataclass
    class Result:
        """
        Remember what the command function call did
        """
        text: str = ""
        image_sent: bool = False

    class FakeBot:
        """
        Simulate the interface of telegram.Bot
        """
        def __init__(self):
            self.result = Result()

        def send_message(self, _chat_id: int, text: str, *_, **_kwargs):
            """ simulate telegram.Bot.send_message """
            self.result.text += str(text)

        def send_photo(self, _chat_id: int, _fp, **_kwargs):
            """ simulate telegram.Bot.send_photo """
            self.result.image_sent = True

    class FakeMessage:
        """
        Simulate telegram.Update.message
        """
        def __init__(self, msg: str = None):
            self.date = datetime.now().astimezone()
            self.chat_id = 42 | 420
            self.text = msg or 'woah'

    class FakeUpdate:
        """
        Simulate telegram.Update
        """
        def __init__(self, upd_msg: str):
            self.message = FakeMessage(upd_msg)

    @dataclass
    class FakeContext:
        """
        Simulate telegram.ext.CallbackContext
        """
        bot: FakeBot
        args: List[str]

    def fire_cmd(cmd, args: list):
        """
        Construct a bot, attach relevant inputs,
        run the command handler, return the result
        """
        fake_bot = FakeBot()
        handler, *_ = cmd.cmdinfo.handlers(cmd)
        real_fn = handler.callback
        fake_update = FakeUpdate(' '.join(['.', *args]))
        ctx = FakeContext(bot=fake_bot, args=args)

        real_fn(fake_update, ctx)

        return fake_bot.result

    def expect_in_response(content: str, cmd, args: list, msg="EXPECT_RESPONSE test case failed."):
        res = fire_cmd(cmd, args).text
        assert content in res, msg + f"\n\nGot response\n{res}\nWhen \'{content}\' was expected"

    def match_in_response(regexp: str, cmd, args: list, msg="MATCH_REPONSE test case failed"):
        res = fire_cmd(cmd, args).text
        match = re.match(regexp, res, flags=re.IGNORECASE | re.MULTILINE)
        assert match is not None, msg + f"\n\nGot response\n{res}\nNot matching \'{regexp}\'"

    def expect_sent_image(cmd, args: list, msg="EXPECT_IMAGE test failed"):
        res = fire_cmd(cmd, args)
        assert res.image_sent, msg + f"\n\nGot response\n{res.text}"

    def expect_error(callback: Callable, *args, error: Type[Exception] = Exception):
        try:
            callback(*args)
        except Exception as err:
            if isinstance(err, error):
                return True
            raise AssertionError("Wrong exception thrown") from err

        raise AssertionError("No exception thrown")

    def expect_no_error(callback: Callable, *args):
        try:
            callback(*args)
            # ok
        except Exception as err:
            raise AssertionError("Exception thrown on expect_no_error") from err

    # testing hashbert
    bert = HashBert()
    expect_in_response("unyyb", bert.rot, ["13", "hallo"])
    expect_in_response("ot a valid integer", bert.rot, ["hey", "what"])
    expect_in_response("ot enough arguments", bert.rot, ["12"])
    expect_in_response("ot enough arguments", bert.rot, [])

    expect_in_response('598d4c200461b81522a3328565c25f7c', bert.md5, ["hallo"])
    expect_in_response('70b77b7546d42e83139316ec07d04867', bert.sha512, ["hallo"])
    expect_in_response('8J+RjA==', bert.b64enc, ["👌"])
    expect_in_response('👌', bert.b64dec, ["8J+RjA=="])
    expect_in_response('598d4c200461b81522a3328565c25f7c', bert.hashit, ["hallo"])

    bert = AsciiBert()
    match_in_response(r'a\s*\\times\s*b', bert.asciimath, ["a cross b"])

    bert = TexBert()
    match_in_response('.*empty inputs are bad.*', bert.displaytex, [""])
    match_in_response('.*invalid argument format.*', bert.aligntex, ["["])
    match_in_response('.*invalid argument format.*', bert.texraw, ["[x...!!]!"])
    match_in_response('.*unexpected argument.*', bert.texraw, ["[x=88]!"])
    match_in_response('.*lern ma latex.*', bert.texraw, ["[res=10] x"])
    expect_sent_image(bert.tex, ["[res=10] x"])

    bert = InterpRert()
    match_in_response('.*no decodable output.*', bert.brainfuck, ["..."])
    match_in_response('.*x01.*', bert.brainfuck, ["+."])
    match_in_response('TGFKAHHLMPIMO', bert.brainfuck,
                      [">+>->->+>+++++++++[-<[+++++++<]>>++>+>++>]<++.<.-.<-----.<+.>>++..<+.+.+++.>+.<---.++."])
    match_in_response('.*timed out.*', bert.brainfuck, ["+[]"])

    bert = HelpBert()
    match_in_response('.*no further help available.*', bert.help, ["weewieofhweioufh"])
    expect_in_response('<cmd name>', bert.help, [])  # check if escaping works

    # Test ArgParser
    expect_error(lambda: Args.parse("[hello=world]", {'x': Args.T.INT}), error=UnexpectedArgument)
    expect_error(lambda: Args.parse("[]", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_error(lambda: Args.parse("[x", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_error(lambda: Args.parse("[x]", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_error(lambda: Args.parse("[x=]", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_error(lambda: Args.parse("[x=string]", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_error(lambda: Args.parse("[x=", {'x': Args.T.INT}), error=ArgumentFormatError)
    expect_no_error(lambda: Args.parse("[x=0]", {'x': Args.T.INT}))
    expect_no_error(lambda: Args.parse_positional("a, c 112", [Args.T.STR, Args.T.char_in("bcdef"), Args.T.INT]))
    expect_error(
        lambda: Args.parse_positional("b, c, dgef", [Args.T.chars_in("abcdef") for _ in range(3)]),
        error=ArgumentFormatError
    )

    print("Tests executed.\nEverything seems fine (it totally isn't)")


if __name__ == '__main__':
    test()
