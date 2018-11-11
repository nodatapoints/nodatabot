from itertools import chain, cycle
from collections import deque


class Level:
    def __init__(self, depth=0):
        self.depth = depth
        self._winner = None
        self.tiles = None
        if not self.atom:
            self.tiles = [[Level(depth-1) for _ in range(3)] for _ in range(3)]

    def __getitem__(self, pos):
        x, y = pos
        return self.tiles[y][x]

    @property
    def atom(self):
        return self.depth == 0

    @property
    def array(self):
        if self.atom:
            return self.winner

        return [[tile.array for tile in row] for row in self.tiles]

    @staticmethod
    def test_equals(line):
        line = iter(line)

        ref = next(line).winner
        for tile in line:
            if tile.winner != ref:
                return None

        return ref

    @property
    def winner(self):
        if self.atom:
            return self._winner

        lines = (
            *self.tiles,  # horizontal
            *zip(*self.tiles),  # vertical (transposed)
            (self.tiles[i][i] for i in range(3)),  # diagonals
            (self.tiles[i][2-i] for i in range(3)),
        )

        # Yay, Python!
        self._winner = next(filter(None, map(self.test_equals, lines)), None)
        return self._winner

    @winner.setter
    def winner(self, w):
        self._winner = w

    @property
    def terminated(self):
        if self.atom:
            return self.winner is not None

        if self.winner is not None:
            return True

        return all(tile.terminated for tile in chain(*self.tiles))


class Game:
    def __init__(self, players, depth=3):
        self.players = cycle(players)
        self.n_players = len(players)
        self.current_player = next(self.players)
        self.root_level = Level(depth)
        self.choice_queue = deque(maxlen=depth-1)

    def get_head_level(self):
        parent = self.root_level
        i = None
        for i, level in enumerate(self.level_queue()):
            if level.terminated:
                return i-1, parent

            parent = level

        return i, level  # FIXME level might be referenced before assignment!

    def level_queue(self):
        yield from self.follow_path(self.choice_queue)

    def follow_path(self, path, include_root=True):
        level = self.root_level
        if include_root:
            yield level

        for choice in path:
            level = level[choice]
            yield level

    @property
    def player_order(self):
        return [next(self.players) for _ in range(self.n_players)]

    @property
    def expected_player(self):
        return self.player_order[0]  # TODO unschön

    def push_choice(self, choice):
        i, level = self.get_head_level()
        if level.terminated:
            self.choice_queue[i] = choice

        self.choice_queue.append(choice)
        if level[choice].atom:
            level[choice].winner = next(self.players)

    def render_keyboard(self, keyboard_class, button_class):
        query = []
        _, head = self.get_head_level()
        for y, row in enumerate(head.tiles):
            query_row = []
            for x, tile in enumerate(row):
                if tile.terminated:
                    button = button_class(
                        tile.winner or ' ',
                        callback_data='invalid'
                    )

                else:
                    button = button_class(' ', callback_data=repr((x, y)))

                query_row.append(button)

            query.append(query_row)

        return keyboard_class(query)
