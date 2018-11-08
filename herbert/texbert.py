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
            )
            image_path = result.stdout.strip()
            self.send_photo_from_file(image_path)

        except CalledProcessError:
            raise Herberror('Lern mal LaTeX 🙄')

        except FileNotFoundError:
            raise Herberror('`textit.zsh` ist immernoch kaputt 😢')

    @command(pass_string=True)
    def tex(self, string, invert=False):
        self.texraw(template.format(string), invert)

    @aliases('dtex')
    @command(pass_string=True)
    def displaytex(self, string):
        self.tex(f'$\\displaystyle {string}$')

    @aliases('itex')
    @command(pass_string=True)
    def inverttex(self, string):
        self.tex(string, invert=True)
