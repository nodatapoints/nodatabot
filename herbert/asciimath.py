import re

from texbert import TexBert
from decorators import command, aliases


EXPR = "(-?[\w\d]+|[{(].+?[})])"


substitutions = {
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


class AsciiBert(TexBert):
    @aliases('am')
    @command(pass_string=True)
    def asciimath(self, string):
        for pattern, subst in substitutions.items():
            string = re.sub(pattern, subst, string)

        self.displaytex(string)
        self.send_message(string, parse_mode=None)
