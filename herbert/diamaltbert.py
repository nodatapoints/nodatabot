from functools import lru_cache
import random

from PIL import Image, ImageOps

from decorators import command, aliases
from basebert import ImageBaseBert, Herberror

'''
Meine Datei zum malen von coolen Sachen
- Philip
'''

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


class DiaMaltBert(ImageBaseBert):
    #todo game of life
    # kp wann

    @aliases('hrrule', 'hrr')
    @command
    def higresrule(self, args):
        """
        Sends the high resolution time diagram as a file
        """
        self.rule(args, full=True)

    @command
    def rule(self, args, full=False):
        """
        Draws a time diagram of a 1D cellular Automaton
        """
        # /rule {t(orus), b(lack), w(hite)} {scale} {r,0,1,2,3,...,255?} {width} {time} {r,[a1,a2,a3,...,awidth} 
        # possible TODO: allow larger rules
        edge = args.pop(0);
        if args[1] == 'r':
            args[1] = random.randint(0,255)
            self.send_message(args[1])
        try:
            scale, num, width, time = map(int, args[:4])
            if scale < 5: raise Herberror('too small')
            if args[4] == 'r':
                setup = [random.randint(0, 1) for _ in range(width)]
            else:
                _, _, _, _, *setup = map(int, args)  # map(int, args[3:]) funkt nicht
            for s in setup:
                if s is not 0 and s is not 1:
                    raise Herberror('Not a valid setup')
            if num >= 2**(2**3):
                raise Herberror("first number must be smaller than 256")
        except Exception as e:
            if issubclass(e.__class__, Herberror):
                raise e
            raise Herberror("Not a valid input\ngehdsch vergrabn")

        # maybe make this a bit nicer
        # its only the binary rep of num in a list
        subrules = []
        i = 2**(2**3)
        while i > 1:
            i = int(i/2)
            tru = int(num/i)
            num -= tru*i
            subrules += [tru]
        subrules = list(reversed(subrules))

        tsteps = [None] * time  # meh :/
        tsteps[0] = setup
        for tstep in range(time-1):
            tsteps[tstep+1] = self.do_rule(tsteps[tstep], subrules, edge)

        img = Image.new('RGB', (width*scale, time*scale))
        pixels = img.load()  # create the pixel map

        # Ja, aua, mach halt besser
        # hier geht nich so schön rekursiv
        # ggf iwas mit x in tsteps oder so
        for bx in range(width):
            for by in range(time):
                color = black
                if tsteps[by][bx] == 0:
                    color = white
                for sx in range(scale):
                    for sy in range(scale):
                        pixels[bx*scale+sx, by*scale+sy] = color
        self.send_pil_image(img, full=full)

    @staticmethod
    def do_rule(last, subrules, edge):
        current = []

        for element in range(len(last)):
            # todo, more abstraction
            # %len(last): blame python that -10 is allowed, but not len+9
            tempel = element

            # todo make nicer   
            if edge is "t": rl = last[(tempel+1)%len(last)] + 2*last[(tempel)%len(last)] + 4*last[(tempel-1)%len(last)]
            elif tempel is 0:
                if edge is "b": rl = last[(tempel+1)%len(last)] + 2*last[(tempel)%len(last)] + 4
                else: rl = last[(tempel+1)%len(last)] + 2*last[(tempel)%len(last)]
            elif tempel is len(last)-1:
                if edge is "b": rl = 1 + 2*last[(tempel)%len(last)] + 4*last[(tempel-1)%len(last)]
                else: rl = 2*last[(tempel)%len(last)] + 4*last[(tempel-1)%len(last)]
            else: rl = last[(tempel+1)%len(last)] + 2*last[(tempel)%len(last)] + 4*last[(tempel-1)%len(last)]

            if subrules[rl] is 1:
                current += [1]
            else:
                current += [0]

        return current

    @command
    def carpet(self, args):
        """
        Generate a self-similar fractal carpet based on the given parameters
        """
        scale, depth, width, height = map(int, args[:4])
        matrix = args[4:]
        if max(width, height)**depth > 5000:
            raise Herberror("zu dick, keinen Bock")

        if len(matrix) != width*height:
            raise Herberror("Angaben nicht valide")

        itmatrix = iter(matrix)
        base = tuple(tuple(next(itmatrix) for _ in range(width)) for _ in range(height))

        self.send_pil_image(self.carpet_recursive(base, depth, scale))

    @lru_cache(256)
    def carpet_recursive(self, matrix, depth, scale, entry=COPY):
        """
        Returns an Image object containing the corresponding carpet image.

        matrix: 2D-List of dimensions n*m containing the recursive structure
                encoded in entries of either 0, 1, 2, or 3
        """
        if depth == 0:
            return Image.new('RGB', (scale, scale), atom_colors(entry))

        width = len(matrix[0])**(depth - 1)*scale
        height = len(matrix)**(depth - 1)*scale

        big_image = Image.new('RGB', (width * len(matrix[0]), height * len(matrix)), atom_colors(entry))
        if entry in (BLACK, WHITE):
            return big_image

        for y, row in enumerate(matrix):
            for x, new_entry in enumerate(row):
                img = self.carpet_recursive(matrix, depth - 1, scale, new_entry)
                big_image.paste(img, (x * width, y * height))

        method = None
        for s in entry:
            method = do_things_to_img.get(s)
        if method is not None:
            big_image = big_image.transpose(method)

        if INVERT in entry:
            big_image = ImageOps.invert(big_image)

        return big_image
