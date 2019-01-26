from subprocess import run, CalledProcessError

from PIL import Image, ImageOps

from decorators import command, aliases
from basebert import ImageBaseBert, Herberror

template = """
\\documentclass[preview, margin=1mm]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{wasysym}}
\\usepackage{{marvosym}}
\\usepackage{{mathtools}}
\\usepackage{{etoolbox}}
\\usepackage{{tikz}}

\\usepackage{{amsfonts}}
\\usepackage[ngerman]{{babel}}

\\usepackage[utf8]{{inputenc}}
\\begin{{document}}
{} % This is where the code goes
\\end{{document}}
"""

min_dimension = 100  # pixels


class TexBert(ImageBaseBert):
    @command(pass_string=True)
    def texraw(self, string, resolution=900, invert=False):
        """
        Render LaTeX
        """
        if string == "":
            raise Herberror('Keine leeren Inputs')
        try:
            result = run(
                ('./texit.zsh', f'{resolution:d}'),
                input=string,
                text=True,
                encoding='utf8',
                capture_output=True,
                check=True
            )  # FIXME unexpected arguments
            image_path = result.stdout.strip()
            img = Image.open(image_path)
            if min(img.width, img.height) < min_dimension:
                self.texraw(
                    string,
                    resolution=2*resolution,
                    invert=invert
                )
                return

            if invert:
                img = ImageOps.invert(img)

            self.send_pil_image(img)

        except CalledProcessError:
            raise Herberror('Lern mal LaTeX 🙄')

        except FileNotFoundError:
            raise Herberror('`texit.zsh` ist immernoch kaputt 😢')

    @command(pass_string=True)
    def tex(self, string, invert=False):
        """
        Render LaTeX. Implies a minimal preamble.
        """
        self.texraw(template.format(string), invert=invert)

    @aliases('dtex')
    @command(pass_string=True)
    def displaytex(self, string):
        """
        Render LaTeX in math-mode. Implies an environment for typesetting math.
        """
        self.tex(f'$\\displaystyle {string}$')

    @aliases('itex')
    @command(pass_string=True)
    def inverttex(self, string):
        """
        Render LaTeX like /tex, but invert the colors.
        """
        self.tex(string, invert=True)

    @aliases('idtex')
    @command(pass_string=True)
    def invertdisplaytex(self, string):
        """
        Render LaTeX like /displaytex, but invert the colors.
        """
        self.tex(f'$\\displaystyle {string}$', invert=True)
