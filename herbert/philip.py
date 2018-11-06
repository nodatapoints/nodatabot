# das is die Datei in der ich Sachen implementiere (also ich bin Philip, duh)
from functools import lru_cache
from urllib.parse import quote

from PIL import Image, ImageOps
from io import BytesIO

from decorators import command, aliases
from basebert import BaseBert, Herberror
from hercurles_network import _t_load_content


black = 0, 0, 0
gray = 123, 123, 123
white = 255, 255, 255

WHITE = 'w'
BLACK = 'b'
ROTATE_LEFT = 'l'
ROTATE_RIGHT = 'r'
ROTATE_180 = 'p'
FLIP_HORIZONTAL = 'h'
FLIP_VERTICAL = 'v'
TRANSPOSE = 't'
INVERT = 'i'
COPY = 'c'

do_things_to_img = {
    ROTATE_LEFT: Image.ROTATE_90,
    ROTATE_RIGHT: Image.ROTATE_270,
    ROTATE_180: Image.ROTATE_180,
    FLIP_HORIZONTAL: Image.FLIP_LEFT_RIGHT,
    FLIP_VERTICAL: Image.FLIP_TOP_BOTTOM,
    TRANSPOSE: Image.TRANSPOSE
}


def atom_colors(entry):
    return white if WHITE in entry or INVERT in entry else black


class PhilipBert(BaseBert):
    @aliases('wa', 'wolframalpha')
    @command
    def wolfram(self, args, full=False):
        query = quote(''.join(args), safe='')
        url = f'https://api.wolframalpha.com/v1/simple?i={query}&appid=36GXXR-K5UA8L8XTY'
        _, data = _t_load_content(url)

        image = Image.open(BytesIO(data))
        self.send_pil_image(image, full)

    @aliases('hrwa')
    @command
    def highreswolfram(self, args):
        self.wolfram(args, full=True)

    @command
    def carpet(self, args):
        scale, depth, width, height = map(int, args[:4])
        matrix = args[4:]
        if max(width, height)**depth > 5000:
            raise Herberror("zu dick, keinen Bock")

        if len(matrix) != width*height:
            raise Herberror("Angaben nicht valide")

        itmatrix = iter(matrix)
        base = tuple(tuple(next(itmatrix) for x in range(width)) for y in range(height))

        self.send_pil_image(self.carpet_recursive(base, depth))

    @lru_cache(256)
    def carpet_recursive(self, matrix, depth, entry=COPY):
        """
        Returns an Image object containing the corresponding carpet image.

        matrix: 2D-List of dimensions n*m containing the recursive structure
                encoded in entries of either 0, 1, 2, or 3

        """     
        if depth == 0:
            return Image.new('RGB', (1, 1), atom_colors(entry))

        width = len(matrix[0])**(depth - 1)
        height = len(matrix)**(depth - 1)

        big_image = Image.new('RGB', (width * len(matrix[0]), height * len(matrix)), atom_colors(entry))
        if entry in (BLACK, WHITE):
            return big_image

        for y, row in enumerate(matrix):
            for x, new_entry in enumerate(row):
                img = self.carpet_recursive(matrix, depth - 1, new_entry)
                big_image.paste(img, (x * width, y * height))

        for s in entry:
            method = do_things_to_img.get(s)
            if method is not None:
                big_image = big_image.transpose(method)

        if INVERT in entry:
            big_image = ImageOps.invert(big_image)

        return big_image

    @command
    def math(self, args):
        args = "".join(args)
        allowed_chars = set('1234567890.+*-/xyz=()')
        if set(args).issubset(allowed_chars):
            try:
                self.send_message(eval(args), {}, {})
            except Exception:
                raise Herberror('not a working equation')
        else: raise Herberror('Dude, NO arbitrary code exec')
