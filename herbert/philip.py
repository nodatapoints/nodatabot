# das is die Datei in der ich Sachen implementiere (also ich bin Philip, duh)
from PIL import Image, ImageOps
from functools import lru_cache
from herbert_utils import *

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


@command_handler('carpet', pass_args=True)
@bot_proxy
def carpet_init(bot, update, args):
    scale, depth, width, height = map(int, args[:4])
    matrix = args[4:]
    if max(width, height)**depth > 5000:
        raise Herberror("zu dick, keinen Bock")

    if len(matrix) != width*height:
        raise Herberror("Angaben nicht valide")

    itmatrix = iter(matrix)
    base = tuple(tuple(next(itmatrix) for x in range(width)) for y in range(height)) 
    carpet(base, depth).save('carpet.png')
    bot.send_photo(update.message.chat_id, open('carpet.png', 'rb'))


@lru_cache(256)
def carpet(matrix, depth, entry=COPY):
    """
    Returns an Image object containing the corresponding carpet image.

    matrix: 2D-List of dimensions n*m containing the recursive structure
            encoded in entries of either 0, 1, 2, or 3
    /([bw]|[rlp]?[hvt]?[ic])/
    
    bw ->
    rlphvt abarbeiten
    i ->
    (c)

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
            img = carpet(matrix, depth - 1, new_entry)
            big_image.paste(img, (x * width, y * height))
    
    for s in entry:
       method = do_things_to_img.get(s)
       if method is not None:
           big_image = big_image.transpose(method)
            
    if INVERT in entry:
        ImageOps.invert(big_image)

    return big_image


@command_handler('math', pass_args=True)
def philip_math(bot,update,args):
    # is the operand valid?
    arg = args.pop(0)
    if arg == '+': res = 0
    elif arg == '*': res = 1
    else: 
        raise Herberror(update.message.chat_id, text="kein valider Operator")
    # are all numbers really numbers?
    try:
        for x in range(len(args)): 
            y = float(args[x])
            if arg == '+': res += y
            elif arg == '*': res *= y
    except ValueError:
        raise Herberror(update.message.chat_id, text="keine validen Zahlen")
    bot.send_message(update.message.chat_id, text=str(res))   

