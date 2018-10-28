from PIL import Image, ImageDraw
from functools import wraps

atom_size = 48
background = 255, 255, 255, 255
padding = 2
resampling_factor = 2

colors = {
    'a': (255, 0, 0),
    'b': (0, 255, 0),
    'c': (0, 0, 255),
    None: (150, 150, 150)
}

line_color = 200, 200, 200
widths = 0, 2, 6, 12, 12
winner_alpha = 80
highlight_alpha = 160


def antialias(draw_func):
    @wraps(draw_func)
    def antialiased(*args, **kwargs):
        image = draw_func(*args, **kwargs)
        size = image.width//resampling_factor, image.height//resampling_factor
        return image.resize(size, resample=Image.ANTIALIAS)

    return antialiased


def draw_level(level, highlights={}):
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
    draw = ImageDraw.Draw(image, 'RGBA')

    for y, row in enumerate(level.tiles):
        for x, tile in enumerate(row):
            image.paste(
                im=draw_level(tile, highlights=highlights),
                box=(x*tile_size + x*w, y*tile_size + y*w)
            )

    if level.terminated:
        color = colors[level.winner] + (winner_alpha, )
        draw.ellipse(xy=(w, w, size-w, size-w), fill=color)

    if level in highlights:
        draw.rectangle(
            xy=(0, 0, size, size),
            outline=highlights[level],
            width=widths[level.depth+1]
        )

    return image


@antialias
def draw_game(game):
    highlights = {}
    queue = list(game.choice_queue)
    for i, player in enumerate(game.player_order[:-1]):
        for level in game.follow_path(queue[i:]):
            pass

        highlights[level] = colors[player] + (highlight_alpha, )

    return draw_level(game.root_level, highlights=highlights)
