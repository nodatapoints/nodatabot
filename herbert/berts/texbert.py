"""
Bert

allows rendering latex to images

provided commands:
    - texraw
    - tex
    - dtex
    - atex
    - itex
    - idtex
    - iatex
"""
import logging
from subprocess import run

from PIL import Image, ImageOps

from basebert import ImageBaseBert
from herberror import Herberror, BadHerberror
from common import chatformat
from common.argparser import Args
from common.constants import SEP_LINE
from common.telegram_limits import IMG_MAX_ASPECT
from decorators import command, aliases, doc

# format breaks here because e.g. {{amsfonts}} gets transformed to {amsfonts} and then the
# real substiture will throw a KeyError

EMPTY_TEX_TEMPLATE = """{}"""
VERY_BASIC_TEX_TEMPLATE = """
\\documentclass[preview, margin=1mm]{{standalone}}
{}
"""
PACKAGES_TEX_TEMPLATE = VERY_BASIC_TEX_TEMPLATE.replace("{}", """
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{wasysym}}
\\usepackage{{marvosym}}
\\usepackage{{mathtools}}
\\usepackage{{etoolbox}}
\\usepackage{{tikz}}
\\usepackage{{physics}}
\\usepackage{{ifthen}}
\\usepackage[hidelinks]{{hyperref}}

\\usepackage{{amsfonts}}
\\usepackage[ngerman]{{babel}}

\\usepackage[utf8]{{inputenc}}
{}
""")
BASIC_TEX_TEMPLATE = PACKAGES_TEX_TEMPLATE.replace("{}", """
\\begin{{document}}
{} % This is where the code goes
\\end{{document}}
""")
DISPLAY_MATH_TEMPLATE = BASIC_TEX_TEMPLATE.replace("{}", """{{$\\displaystyle {}$}}""")
ALIGNED_MATH_TEMPLATE = DISPLAY_MATH_TEMPLATE.replace("{}", """{{\\begin{{aligned}} {} \\end{{aligned}} }}""")

TIKZ_TEMPLATE = PACKAGES_TEX_TEMPLATE.replace("{}", """
\\usetikzlibrary{{shapes,arrows}}
\\begin{{document}}
\\begin{{tikzpicture}}
{}
\\end{{tikzpicture}}
\\end{{document}}
""")

pre_levels = [EMPTY_TEX_TEMPLATE,
              VERY_BASIC_TEX_TEMPLATE,
              PACKAGES_TEX_TEMPLATE,
              BASIC_TEX_TEMPLATE,
              DISPLAY_MATH_TEMPLATE,
              ALIGNED_MATH_TEMPLATE,
              TIKZ_TEMPLATE]


def validate(string):
    """
    If the input can reasonably be handed off to latex,
    do nothing, otherwise throw an appropriate error
    """
    if string.strip() == '':
        raise Herberror('Empty Inputs are bad.')


class TexBert(ImageBaseBert):
    """
    Bert for rendering latex code
    See `TexBert.texraw`
    """

    @command(pass_string=True)
    @doc(
        f"""
        Render LaTeX

        Writes the given string into a file, runs a latex compiler on it and returns the result.

        TeX is a turing-complete macro markup language, suited especially for typesetting mathematical equations. \
        For more information, syntax and general help try consulting the internet.

        If the argument starts with '[', everything up to the next ']' is interpreted as configuration options for the \
        rendering itself, not as tex source code.

        Valid options are
        m§pre§ (integer value, range 0-{len(pre_levels) - 1}) - setup a tex environment.
        m§inv§ (boolean value) - invert the colors of the output image
        m§res§ (integer value) - width of the output image in pixels
        m§send§ (either img or file or both or validate) - decide which information to return

        The pre-environments available are:
        0: nothing
        1: documentclass standalone
        2: packages (mathsstuff, tikz, ifthen)
        3: packages + begin document
        4: display math environment
        5: aligned multiline display math environment
        6: tikzimage environment
        
        Try
        m§/tex [pre=5, inv=yes, send=both] x &= y \\\\ &= z §
        m§/dtex [res=1000, inv=false] \\sum §
        """
    )
    def texraw(self, string, invert=False, pre_level=None):
        argvals, string = Args.parse(string, {
            'inv': Args.T.BOOL,
            'send': Args.T.one_of('img', 'file', 'both', 'validate'),
            'res': Args.T.INT,
            'pre': Args.T.INT.bounded(0, len(pre_levels)),
            # 'err':    Args.T.one_of('last', 'all'), TODO
            # 'format': Args.T.one_of('img', 'pdf', 'dvi') TODO
        })

        validate(string)

        pre_level = pre_level or argvals.get('pre') or 0
        template = pre_levels[pre_level]

        string = template.format(string)

        target_pixel_width = argvals.get('res') or 1000
        if target_pixel_width > 5000:
            raise Herberror('Dude wtf are you doing?')

        try:
            result = run(
                ('./ext/texit.zsh', f'{target_pixel_width:d}'),
                input=string,
                encoding='utf8',
                capture_output=True,
                check=False
            )
            exit_val = result.returncode

            if exit_val == 2:
                logging.getLogger('herbert.RUNTIME').warning('Couldn\'t cleanup working directory.')
            elif exit_val == 3:
                raise Herberror('Your \'tex produces output I literally can\'t comprehend.')
            elif exit_val == 4:
                raise Herberror(f'Lern ma LaTeX 🙄\n{SEP_LINE}\n'
                                f'[{chatformat.bold("LATEX")}] {chatformat.mono(result.stdout)}')
            elif exit_val != 0:
                raise BadHerberror('Error. That was unexpected.')

            # exit_val is 0 or 2, main.png _should_ exist at this point
            image_path = result.stdout.strip()
            img = Image.open(image_path)

            if img.width / img.height > IMG_MAX_ASPECT:
                buf = Image.new(mode='RGB', size=(img.width, int(img.width / IMG_MAX_ASPECT + 1)),
                                color=(255, 255, 255))
                buf.paste(img)
                img = buf

            if invert or argvals.get('inv'):
                img = ImageOps.invert(img.convert(mode='RGB'))

            arg_send = argvals.get('send') or 'img'
            if arg_send in ('file', 'both'):
                self.send_pil_image(img, full=True)
            if arg_send in ('img', 'both'):
                self.send_pil_image(img)

        except FileNotFoundError as err:
            raise BadHerberror('`texit.zsh` is broken 😢') from err

    @command(pass_string=True)
    @doc(
        """
        Render LaTeX. Implies a minimal preamble.

        This is an alias for m§/texraw [pre=2]§. For more information look at m§/help§ texraw.

        e.g: m§/tex Hello World!§
        """
    )
    def tex(self, string, invert=False):
        self.texraw(string, invert=invert, pre_level=3)

    @aliases('dtex')
    @command(pass_string=True)
    @doc(
        """
        Render LaTeX in math-mode. Implies an environment for typesetting math.

        This is an alias for m§/texraw [pre=3]§. For more information look at m§/help§ texraw.

        e.g: m§/dtex \\sum_{n=1}^\\infty \\frac{1}{n^2}§
        """

    )
    def displaytex(self, string, invert=False):
        self.texraw(string, invert=invert, pre_level=4)

    @aliases('atex')
    @command(pass_string=True)
    @doc(
        """
        Render LaTeX in aligned math-mode. Implies an environment for typesetting math.

        This is an alias for m§/texraw [pre=4]§. For more information look at m§/help§ texraw.

        e.g: m§/atex a&=b&\\text{weil }c\\\\&=d§
        """
    )
    def aligntex(self, string, invert=False):
        self.texraw(string, invert=invert, pre_level=5)

    @aliases('itex')
    @command(pass_string=True)
    @doc(
        """
        Render LaTeX like /tex, but invert the colors.

        This is an alias for m§/texraw [pre=2, inv=true]§. For more information look at m§/help§ texraw.

        e.g: m§/itex pure white§
        """
    )
    def inverttex(self, string):
        self.tex(string, invert=True)

    @aliases('idtex')
    @command(pass_string=True)
    @doc(
        """
        Render LaTeX like /displaytex, but invert the colors.

        This is an alias for m§/texraw [pre=3, inv=true]§. For more information look at m§/help§ texraw.

        e.g: m§/idtex \\text{\\#ffffff} = \\blacksquare§
        """
    )
    def invertdisplaytex(self, string):
        self.displaytex(string, invert=True)

    @aliases('iatex')
    @command(pass_string=True)
    @doc(
        """
        Render LaTeX like /aligntex, but invert the colors

        This is an alias for /m§texraw [pre=4, inv=true]§. For more information look at m§/help§ texraw.

        e.g: m§/iatex a&=b&\\text{weil }c\\\\&=d§
        """
    )
    def invertaligntex(self, string):
        self.aligntex(string, invert=True)
