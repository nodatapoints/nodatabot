from basebert import BaseBert
from decorators import command, aliases
from subprocess import CalledProcessError

import re
import texbert


EXPR = "(-?[\w\d]+|[{(].+?[})])"


_substitutions = {
    "\s+": " ",  # first, remove regular whitespace
    "\s*([+*-/,.)(<>=])\s*": "\\1",  # then, around operators
    "->": "\\\\rightarrow ",
    "<=>": "\\\\iff ",
    "=>": "\\\\implies ",
    "inf": "\\\\infty ",
    "\\sin\\s": "\\\\in ",
    "N": "\\\\mathbb{N}",
    "R": "\\\\mathbb{R}",
    "Q": "\\\\mathbb{Q}",
    EXPR + "\\^" + EXPR: "{{\\1}^{\\2}}",
    EXPR + "/" + EXPR: "{\\\\frac{\\1}{\\2}}",
    "lim\\s*" + EXPR: "{\\\\lim_{\\1}}",
    "\\*": "\\\\cdot ",
    "O": "\\\\mathcal{O}",
    "P": "\\\\mathcal{P}",
    "\\(": "\\\\left(",
    "\\)": "\\\\right)"
}


class AsciiBert(BaseBert):
    @aliases('am')
    @command(pass_string=True)
    def asciimath(self, string):
        for m in _substitutions:
            string = re.sub(m, _substitutions[m], string)

        tech = texbert.TexBert()  # this is wrong on so many levels
        tech.bot, tech.update = self.bot, self.update  # PLEASE provide renderTex() as a nonmember
        tech.displaytex(string)  # oh god it hurts so much

        self.send_message(string, parse_mode=None)
