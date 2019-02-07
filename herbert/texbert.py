from subprocess import run, CalledProcessError

from PIL import Image, ImageOps

from decorators import command, aliases
from basebert import ImageBaseBert, Herberror, BadHerberror
from common.argparser import Args

import logging
import re

very_basic_tex_template = """
\\documentclass[preview, margin=1mm]{{standalone}}
{}
"""

basic_tex_template = """
\\documentclass[preview, margin=1mm]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{wasysym}}
\\usepackage{{marvosym}}
\\usepackage{{mathtools}}
\\usepackage{{etoolbox}}
\\usepackage{{tikz}}
\\usepackage{{physics}}

\\usepackage{{amsfonts}}
\\usepackage[ngerman]{{babel}}

\\usepackage[utf8]{{inputenc}}
\\begin{{document}}
{} % This is where the code goes
\\end{{document}}
"""

# format breaks here because e.g. {{amsfonts}} gets transformed to {amsfonts} and then the
# real substiture will throw a KeyError
display_math_template = basic_tex_template.replace("{}", """{{$\\displaystyle {}$}}""")
aligned_math_template = display_math_template.replace("{}", """{{\\begin{{aligned}} {} \\end{{aligned}} }}""")


def validate(str):
    # TODO make sure people dont tex emojis or whatever
    if str.strip() == '':
        raise Herberror('Empty Inputs are bad.')


class TexBert(ImageBaseBert):
    @command(pass_string=True)
    def texraw(self, string, invert=False, template="{}"):
        """
        Render LaTeX
        """
        argvals, string = Args.parse(string, {
            'inv':    Args.T.BOOL,
            # 'send':   Args.T.one_of('file', 'both', 'validate'), TODO
            'res':    Args.T.INT,
            'pre':    Args.T.bounded(Args.T.INT, limits=(0, 4)),
            # 'err':    Args.T.one_of('last', 'all'), TODO
            # 'format': Args.T.one_of('pdf', 'dvi') TODO
        })

        argvals = argvals or dict()
        validate(string)

        pre_level = argvals.get('pre')
        if pre_level is not None:
            if pre_level == 0:
                template = "{}"
            elif pre_level == 1:
                template = very_basic_tex_template
            elif pre_level == 2:
                template = basic_tex_template
            elif pre_level == 3:
                template = display_math_template
            elif pre_level == 4:
                template = aligned_math_template

        string = template.format(string)

        target_pixel_width = argvals.get('res') or 1000
        if target_pixel_width > 1e5:
            raise Herberror('Dude wtf are you doing?')



        try:
            result = run(
                ('./texit.zsh', f'{target_pixel_width:d}'),
                input=string,
                encoding='utf8',
                capture_output=True
            )
            exit_val = result.returncode

            if exit_val == 2:
                logging.info(f'Couldn\'t cleanup directory {result.stdout}.')
            elif exit_val == 3:
                raise Herberror('Your \'tex produces output I literally can\'t comprehend.')
            elif exit_val == 4:
                raise Herberror('Lern ma LaTeX 🙄')
            elif exit_val != 0:
                raise BadHerberror('Error. That was unexpected.')

            # exit_val is 0 or 2, main.png _should_ exist at this point
            image_path = result.stdout.strip()
            img = Image.open(image_path)

            if img.width / img.height > 20.0:
                buf = Image.new(mode='RGB', size=(img.width, int(img.width/20.0 + 1)), color=(255, 255, 255))
                buf.paste(img)
                img = buf

            if invert or argvals.get('inv'):
                img = ImageOps.invert(img.convert(mode='RGB'))

            self.send_pil_image(img)

        except FileNotFoundError:
            raise BadHerberror('`texit.zsh` is broken 😢')

    @command(pass_string=True)
    def tex(self, string, invert=False):
        """
        Render LaTeX. Implies a minimal preamble.
        """
        validate(string)
        self.texraw(string, invert=invert, template=basic_tex_template)

    @aliases('dtex')
    @command(pass_string=True)
    def displaytex(self, string, invert=False):
        """
        Render LaTeX in math-mode. Implies an environment for typesetting math.
        """
        validate(string)
        self.texraw(string, invert=invert, template=display_math_template)

    @aliases('atex')
    @command(pass_string=True)
    def aligntex(self, string, invert=False):
        """
        Render LaTeX in aligned math-mode. Implies an environment for typesetting math.
        """
        validate(string)
        self.texraw(string, invert=invert, template=aligned_math_template)

    @aliases('itex')
    @command(pass_string=True)
    def inverttex(self, string):
        """
        Render LaTeX like /tex, but invert the colors.
        """
        validate(string)
        self.tex(string, invert=True)

    @aliases('idtex')
    @command(pass_string=True)
    def invertdisplaytex(self, string):
        """
        Render LaTeX like /displaytex, but invert the colors.
        """
        validate(string)
        self.displaytex(string, invert=True)

    @aliases('iatex')
    @command(pass_string=True)
    def invertedaligntex(self, string):
        """
        Render LaTeX like /algintex, but invert the colors
        """
        validate(string)
        self.aligntex(string, invert=True)
