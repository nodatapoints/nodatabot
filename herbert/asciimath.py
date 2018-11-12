from basebert import BaseBert
from decorators import command, aliases

import re
import texbert


EXPR = r'(-?[\w\d]+|\([^()]*\)|{[^{}]+?})'


_substitutions = {
    r'\s+': r' ',  # first, remove regular whitespace
    r'\s*([+*-/,.)(<>=])\s*': r'\1',  # then, around operators
    r'->': r'\\rightarrow ',
    r'<=>': r'\\iff ',
    r'=>': r'\\implies ',
    r'inf': r'\\infty ',
    r'\sin\s': r'\\in ',
    r'N': r'\\mathbb{N}',
    r'R': r'\\mathbb{R}',
    r'Q': r'\\mathbb{Q}',
    EXPR + r'\^' + EXPR: r'{{\1}^{\2}}',
    EXPR + r'/' + EXPR: r'{\\frac{\1}{\2}}',
    r'lim\s*' + EXPR: r'{\\lim_{\1}}',
    r'\*': r'\\cdot ',
    r'O': r'\\mathcal{O}',
    r'P': r'\\mathcal{P}',
    r'\(': r'{\\left(',
    r'\)': r'\\right)}'
}


class AsciiBert(BaseBert):
    @aliases('am')
    @command(pass_string=True)
    def asciimath(self, string):
        for m in _substitutions:
            print(string)
            string = re.sub(m, _substitutions[m], string)

        tech = texbert.TexBert()  # this is wrong on so many levels
        tech.bot, tech.update = self.bot, self.update  # PLEASE provide renderTex() as a nonmember
        tech.displaytex(string)  # oh god it hurts so much

        self.send_message(string, parse_mode=None)
