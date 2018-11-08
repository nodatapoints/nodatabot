from subprocess import run, CalledProcessError

from decorators import command
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
{} % This is where the Code goes
\\end{{document}}
"""


class TexBert(BaseBert):
    @command(pass_string=True)
    def tex(self, string):
        code = template.format(string)

        try:
            result = run(
                ('./texit.zsh'),
                input=code,
                text=True,
                encoding='utf8',
                capture_output=True,
                check=True
            )
            image_path = result.stdout.strip()
            self.send_photo_from_file(image_path)

        except CalledProcessError:
            raise Herberror('Lern mal LaTeX 🙄')
