from decorators import command, aliases

import re

from texbert import TexBert

EXPR = r'(-?[\w\d]+|\([^()]*\)|{[^{}]+?})'


_substitutions = {
    r'\s+': r' ',  # first, remove regular whitespace
    r'\s*([+*-/,.)(<>=])\s*': r'\1',  # then, around operators
    r'->': r'\\rightarrow ',
    r'<=>': r'\\iff ',
    r'=>': r'\\implies ',
    r':=': r'\\coloneqq ',
    r'and': r'\\:\\wedge\\: ',
    r'or': r'\\:\\vee\\: ',
    r'not': r'\\neg ',
    r'inf': r'\\infty ',
    r'pi': r'\\pi ',
    r'tau': r'\\tau ',
    r'theta': r'\\theta ',
    r'epsilon': r'\\varepsilon ',
    r'sigma': r'\\sigma ',
    r'vec([\w\d]+)': r'\\vec{\1} ',
    r'cross': r'\\times ',
    r'\\sin\s': r'\\in ',
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


class AsciiBert(TexBert):
    @aliases('am')
    @command(pass_string=True)
    def asciimath(self, string):
        """
        Turn your plaintext equations into images

        This is an experimental parser to generate tex code from your mathematical plain-text \
        input, render it and return the image.

        A lot of things aren't working correctly as of now, but it works for simple equations and terms.
        Try, for example
        ` (a + b)^2 `
        ` A and B and not C `
        ` lim {{x->inf}} 1/x `
        ` v cross u * r `
        """
        for pattern, subst in _substitutions.items():
            string = re.sub(pattern, subst, string)

        self.displaytex(string)
        self.send_message(string, parse_mode=None)
