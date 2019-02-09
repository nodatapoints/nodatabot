import re

from common import chatformat
from basebert import BaseBert, Herberror, BadHerberror
from decorators import command, aliases
from datetime import datetime

from asciimath import AsciiBert
from hashbert import HashBert
from helpbert import HelpBert
from interprert import InterpRert
from texbert import TexBert


class TestBert(BaseBert):

    @aliases('dbg_e')
    @command(register_help=False, pass_string=True)
    def debug_error(self, string):
        raise Herberror(string)

    @aliases('dbg_be')
    @command(register_help=False, pass_string=True)
    def debug_bad_error(self, string: str):
        raise BadHerberror(string)

    @aliases('dbg_ue')
    @command(register_help=False, pass_string=True)
    def debug_unexpected_error(self, string: str):
        raise ValueError(string)

    @aliases('dbg_md')
    @command(register_help=False, pass_string=True)
    def dbg_print_formatted(self, string: str):
        self.reply_text(chatformat.bold(string) + chatformat.italic(string) + chatformat.mono(string) + string,
                        parse_mode=chatformat.get_parse_mode())


res = ""
image_sent = False

if __name__ == '__main__':
    """
    UNIT TESTING
    
    just run `python3.7 testbert.py`
    
    there are by no means enough tests to avoid most bugs, but at least this 
    should help to catch some mistakes somewhat easier. please add more tests.
    """
    # WARNING
    # this is kind of a bodge; test at your own risk


    class FakeBot:
        def send_message(self, chat_id: int, text: str, *_, **kwargs):
            global res
            res += str(text)

        def send_photo(self, chat_id: int, fp, **kwargs):
            global image_sent
            image_sent = True  # lol


    class FakeMessage:
        def __init__(self, msg: str = None):
            self.date = datetime.now()
            self.chat_id = 42 | 420
            self.text = msg or 'woah'


    class FakeUpdate:
        def __init__(self, upd_msg: str):
            self.message = FakeMessage(upd_msg)


    fb = FakeBot()

    def fire_cmd(cmd, args: list):
        global res, image_sent
        res = ""
        image_sent = False
        handler = cmd.command_handler('x', cmd)
        real_fn = handler.callback
        fu = FakeUpdate(' '.join(['.', *args]))

        if handler.pass_args:
            real_fn(fb, fu, args)
        else:
            real_fn(fb, fu)

    def expect_in_response(content: str, cmd, args: list, msg="EXPECT_RESPONSE test case failed."):
        global res
        fire_cmd(cmd, args)
        assert content in res, msg + f"\n\nGot response\n{res}\nWhen \'{content}\' was expected"

    def match_in_response(regexp: str, cmd, args: list, msg="MATCH_REPONSE test case failed"):
        global res
        fire_cmd(cmd, args)
        match = re.match(regexp, res, flags=re.IGNORECASE | re.MULTILINE)
        assert match is not None, msg + f"\n\nGot response\n{res}\nNot matching \'{regexp}\'"

    def expect_sent_image(cmd, args: list, msg="EXPECT_IMAGE test failed"):
        global image_sent
        fire_cmd(cmd, args)
        assert image_sent, msg + f"\n\nGot response\n{res}"

    # testing hashbert
    h = HashBert()
    expect_in_response("unyyb", h.rot, ["13", "hallo"])
    expect_in_response("ot a valid integer", h.rot, ["hey", "what"])
    expect_in_response("ot enough arguments", h.rot, ["12"])
    expect_in_response("ot enough arguments", h.rot, [])

    expect_in_response('598d4c200461b81522a3328565c25f7c', h.md5, ["hallo"])
    expect_in_response('70b77b7546d42e83139316ec07d04867', h.sha512, ["hallo"])
    expect_in_response('8J+RjA==', h.b64enc, ["👌"])
    expect_in_response('👌', h.b64dec, ["8J+RjA=="])
    expect_in_response('598d4c200461b81522a3328565c25f7c', h.hashit, ["hallo"])

    h = AsciiBert()
    match_in_response(r'a\s*\\times\s*b', h.asciimath, ["a cross b"])

    h = TexBert()
    match_in_response('.*empty inputs are bad.*', h.displaytex, [""])
    match_in_response('.*invalid argument format.*', h.aligntex, ["["])
    match_in_response('.*invalid argument format.*', h.texraw, ["[x...!!]!"])
    match_in_response('.*unexpected argument.*', h.texraw, ["[x=88]!"])
    match_in_response('.*lern ma latex.*', h.texraw, ["[res=10] x"])
    expect_sent_image(h.tex, ["[res=10] x"])

    h = InterpRert()
    match_in_response('.*no decodable output.*', h.brainfuck, ["..."])
    match_in_response('.*x01.*', h.brainfuck, ["+."])
    match_in_response('TGFKAHHLMPIMO', h.brainfuck,
                      [">+>->->+>+++++++++[-<[+++++++<]>>++>+>++>]<++.<.-.<-----.<+.>>++..<+.+.+++.>+.<---.++."])
    match_in_response('.*timed out.*', h.brainfuck, ["+[]"])

    h = HelpBert()
    match_in_response('.*no further help available.*', h.help, ["weewieofhweioufh"])
    expect_in_response('&lt;cmd name&gt;', h.help, [])  # check if escaping works
    # testing working help is hard because register_bert() isn't executed for this test run

    # TODO test DiaMaltBert
    # TODO test GameBert
    # TODO test kalcbert
    # TODO test todobert (ironic)

    # internet:
    # TODO test hercurles
    # TODO test urbanbert
    # TODO test xkcdert

    print("Tests executed.\nEverything seems fine (it totally isn't)")
