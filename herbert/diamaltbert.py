from functools import lru_cache
import random
from contextlib import suppress
from math import log
from itertools import islice

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
        # /rule {r, t(orus), b(lack), w(hite)} {scale} {r,0,1,2,3,...,255?} {width} {time} {r,[a1,a2,a3,...,awidth} 
        
        # args to parameters
        for to_int in range(len(args)):
            with suppress(ValueError):
                args[to_int] = int(args[to_int])
        edge, scale, num, width, time, *setup = args

        # handle random queries and catch input errors
        if edge is 'r':             edge = random.choice([t,b,w])
        if num is 'r':              num = random.randint(0,255)
        elif num < 0:               raise Herberror('Not a valid rule') 
        if setup[0] is 'r':         setup = [random.randint(0, 1) for _ in range(width)]
        elif len(setup) != width:   raise Herberror('Not a valid setup')
        else: 
            for s, _ in enumerate(setup):
                if setup[s] not in [0,1]:  
                                    raise Herberror('Not a valid setup')

        # gets the binary representation of the String, meh
        rulelength = max(3, int(log(log(max(num,255),2),2))+1)  # how many cells are affecting the next
        subrules = list(f'{num:b}'[::-1])                       # create needed rules
        subrules.extend([0] * (2**rulelength - len(subrules)))  # 0-pad up to the needed size
        subrules = list(map(int,subrules))                      # turn to number[] from string[]

        tsteps = [None]*(time)
        tsteps[0] = setup
        for i in range(time-1):
            tsteps[i+1] = self.do_rule(tsteps[i], subrules, rulelength, edge)

        img = Image.new('RGB', (width*scale, time*scale))
        for y, ey in enumerate(tsteps):
            for x, ex in enumerate(ey):
                if ex is 0: color = white
                else:       color = black
                subimg = Image.new('RGB', (scale, scale), color)
                img.paste(subimg, (x * scale, y * scale))
        self.send_pil_image(img, full=full)

    def do_rule(self, last, subrules, rulelength, edge):
        Δx = -(rulelength//2) 
        current = []

        for index, element in enumerate(last):
            current += [self.do_step(index, last, Δx, rulelength, edge, subrules)]
        return current

    @staticmethod
    def do_step(index, last, Δx, rulelength, edge, subrules):
        pow_of_2 = 1
        output = 0;
        listmax = len(last)
        listmin = 0
        for i in reversed(range(rulelength)):
            if i+index+Δx >= listmin and i+index+Δx < listmax:
                temp_value = last[i+index+Δx]
            else:
                if edge is 't':     temp_value = last[(i+index+Δx)%listmax]
                elif edge is 'w':   temp_value = 0
                elif edge is 'b':   temp_value = 1
                else:               raise Herberror('not a vadid edge-identifier')
            output += pow_of_2 * temp_value
            pow_of_2 *= 2
        return subrules[output]


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
