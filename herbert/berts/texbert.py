import logging
from subprocess import run

from PIL import Image, ImageOps

from basebert import ImageBaseBert, Herberror, BadHerberror
from common import chatformat
from common.argparser import Args
from common.constants import SEP_LINE
from common.telegram_limits import IMG_MAX_ASPECT
from decorators import command, aliases, doc

# format breaks here because e.g. {{amsfonts}} gets transformed to {amsfonts} and then the
# real substiture will throw a KeyError

very_basic_tex_template = """
\\documentclass[preview, margin=1mm]{{standalone}}
{}
"""
packages_tex_template = very_basic_tex_template.replace("{}", """
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{wasysym}}
\\usepackage{{marvosym}}
\\usepackage{{mathtools}}
\\usepackage{{etoolbox}}
\\usepackage{{tikz}}
\\usepackage{{physics}}
\\usepackage{{ifthen}}

\\usepackage{{amsfonts}}
\\usepackage[ngerman]{{babel}}

\\usepackage[utf8]{{inputenc}}
{} 
""")
basic_tex_template = packages_tex_template.replace("{}", """
\\begin{{document}}
{} % This is where the code goes
\\end{{document}}
""")
display_math_template = basic_tex_template.replace("{}", """{{$\\displaystyle {}$}}""")
aligned_math_template = display_math_template.replace("{}", """{{\\begin{{aligned}} {} \\end{{aligned}} }}""")

tikz_template = packages_tex_template.replace("{}", """
\\usetikzlibrary{{shapes,arrows}}
\\begin{{document}}
\\begin{{tikzpicture}}
{}
\\end{{tikzpicture}}
\\end{{document}}
""")

pre_levels = [very_basic_tex_template,
              basic_tex_template,
              display_math_template,
              aligned_math_template,
              tikz_template]


def validate(str):
    # TODO make sure people dont tex emojis or whatever
    if str.strip() == '':
        raise Herberror('Empty Inputs are bad.')


class TexBert(ImageBaseBert):
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
        m§pre§ (integer value, range 0-{len(pre_levels)}) - setup a tex environment. (0 - nothing, \
        4 - aligned block in displaymath in document)
        m§inv§ (boolean value) - invert the colors of the output image
        m§res§ (integer value) - width of the output image in pixels
        m§send§ (either img or file or both or validate) - decide which information to return

        Try
        m§/tex [pre=4, inv=yes, send=both] x &= y \\\\ &= z §
        m§/dtex [res=1000, inv=false] \\sum §
        """
    )
    def texraw(self, string, invert=False, template="{}"):
        argvals, string = Args.parse(string, {
            'inv': Args.T.BOOL,
            'send': Args.T.one_of('img', 'file', 'both', 'validate'),
            'res': Args.T.INT,
            'pre': Args.T.INT.bounded(limits=(0, len(pre_levels))),
            # 'err':    Args.T.one_of('last', 'all'), TODO
            # 'format': Args.T.one_of('img', 'pdf', 'dvi') TODO
        })

        validate(string)

        pre_level = argvals.get('pre') or 0
        if pre_level > 0:
            template = pre_levels[pre_level - 1]
        elif template is None:
            template = "{}"

        string = template.format(string)

        target_pixel_width = argvals.get('res') or 1000
        if target_pixel_width > 5000:
            raise Herberror('Dude wtf are you doing?')

        try:
            result = run(
                ('./ext/texit.zsh', f'{target_pixel_width:d}'),
                input=string,
                encoding='utf8',
                capture_output=True
            )
            exit_val = result.returncode

            if exit_val == 2:
                logging.getLogger('herbert.RUNTIME').warning(f'Couldn\'t cleanup working directory.')
            elif exit_val == 3:
                raise Herberror('Your \'tex produces output I literally can\'t comprehend.')
            elif exit_val == 4:
                raise Herberror(f'Lern ma LaTeX 🙄\n{SEP_LINE}\n'f'[{chatformat.bold("LATEX")}] {chatformat.mono(result.stdout)}')
            elif exit_val != 0:
                raise BadHerberror('Error. That was unexpected.')

            # exit_val is 0 or 2, main.png _should_ exist at this point
            image_path = result.stdout.strip()
            img = Image.open(image_path)

            if img.width / img.height > IMG_MAX_ASPECT:
                buf = Image.new(mode='RGB', size=(img.width, int(img.width / IMG_MAX_ASPECT + 1)), color=(255, 255, 255))
                buf.paste(img)
                img = buf

            if invert or argvals.get('inv'):
                img = ImageOps.invert(img.convert(mode='RGB'))

            arg_send = argvals.get('send') or 'img'
            if arg_send == 'file' or arg_send == 'both':
                self.send_pil_image(img, full=True)
            if arg_send == 'img' or arg_send == 'both':
                self.send_pil_image(img)

        except FileNotFoundError:
            raise BadHerberror('`texit.zsh` is broken 😢')

    @command(pass_string=True)
    def tex(self, string, invert=False):
        """
        Render LaTeX. Implies a minimal preamble.

        This is an alias for /texraw [pre=2]. For more information look at /help texraw.
        """
        self.texraw(string, invert=invert, template=basic_tex_template)

    @aliases('dtex')
    @command(pass_string=True)
    def displaytex(self, string, invert=False):
        """
        Render LaTeX in math-mode. Implies an environment for typesetting math.

        This is an alias for /texraw [pre=3]. For more information look at /help texraw.
        """
        self.texraw(string, invert=invert, template=display_math_template)

    @aliases('atex')
    @command(pass_string=True)
    def aligntex(self, string, invert=False):
        """
        Render LaTeX in aligned math-mode. Implies an environment for typesetting math.

        This is an alias for /texraw [pre=4]. For more information look at /help texraw.
        """
        self.texraw(string, invert=invert, template=aligned_math_template)

    @aliases('itex')
    @command(pass_string=True)
    def inverttex(self, string):
        """
        Render LaTeX like /tex, but invert the colors.

        This is an alias for /texraw [pre=2, inv=true]. For more information look at /help texraw.
        """
        self.tex(string, invert=True)

    @aliases('idtex')
    @command(pass_string=True)
    def invertdisplaytex(self, string):
        """
        Render LaTeX like /displaytex, but invert the colors.

        This is an alias for /texraw [pre=3, inv=true]. For more information look at /help texraw.
        """
        self.displaytex(string, invert=True)

    @aliases('iatex')
    @command(pass_string=True)
    def invertaligntex(self, string):
        """
        Render LaTeX like /aligntex, but invert the colors

        This is an alias for /texraw [pre=4, inv=true]. For more information look at /help texraw.
        """
        self.aligntex(string, invert=True)
