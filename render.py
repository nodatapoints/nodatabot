from PIL import Image, ImageDraw
from functools import wraps

atom_size = 24
background = 255, 255, 255
padding = 2
resampling_factor = 3

colors = {
    'a': (255, 0, 0),
    'b': (0, 255, 0),
    'c': (0, 0, 255)
}

line_color = 200, 200, 200
widths = 0, 1, 3, 6


def antialias(draw_func):
    @wraps(draw_func)
    def antialiased(*args, **kwargs):
        image = draw_func(*args, **kwargs)
        scaled = image.resize(
            (image.width * resampling_factor, image.height * resampling_factor)
        )
        return scaled.resize(image.size, resample=Image.ANTIALIAS)

    return antialiased


@antialias
def draw_level(level):
    # Drawing the lines by not drawing them
    if level.atom:
        image = Image.new('RGB', (atom_size, atom_size), background)
        draw = ImageDraw.Draw(image)

        if level.terminated:
            draw.ellipse(
                xy=(padding, padding, atom_size-padding, atom_size-padding),
                fill=colors[level.winner]
            )

        return image

    w = widths[level.depth]
    tile_size = draw_level(level[0, 0]).width
    size = 3*tile_size + 2*w

    image = Image.new('RGB', (size, size), line_color)
    draw = ImageDraw.Draw(image)

    for y, row in enumerate(level.tiles):
        for x, tile in enumerate(row):
            image.paste(
                im=draw_level(tile),
                box=(x*tile_size + x*w, y*tile_size + y*w)
            )

    return image
