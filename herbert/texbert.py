from subprocess import run, CalledProcessError

from decorators import command, aliases
from basebert import BaseBert, Herberror

template = """
\\documentclass[preview, margin=1mm]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{wasysym}}
\\usepackage{{amsfonts}}
\\usepackage[ngerman]{{babel}}

\\usepackage[utf8]{{inputenc}}
\\begin{{document}}
{} % This is where the code goes
\\end{{document}}
"""


class TexBert(BaseBert):
    @command(pass_string=True)
    def texraw(self, string, invert=False):
        """
        Render LaTeX
        """
        args = ['./texit.zsh']
        if invert:
            args.append('-invert')

        try:
            result = run(
                args,
                input=string,
                text=True,
                encoding='utf8',
                capture_output=True,
                check=True
            )  # FIXME unexpected arguments
            image_path = result.stdout.strip()
            self.send_photo_from_file(image_path)

        except CalledProcessError:
            raise Herberror('Lern mal LaTeX 🙄')

        except FileNotFoundError:
            raise Herberror('`textit.zsh` ist immernoch kaputt 😢')

    @command(pass_string=True)
    def tex(self, string, invert=False):
        """
        Render LaTeX. Implies a minimal preamble.
        """
        self.texraw(template.format(string), invert)

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
