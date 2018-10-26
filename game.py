from itertools import chain, cycle
from collections import deque


class Level:
    def __init__(self, depth=0):
        self.atom = (depth == 0)
        self._winner = None
        self.tiles = None
        if not self.atom:
            self.tiles = [[Level(depth-1) for _ in range(3)] for _ in range(3)]


    def __getitem__(self, pos):
        x, y = pos
        return self.tiles[y][x]

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

        for line in lines:
            self._winner = self._winner or self.test_equals(line)

        return self._winner

    @winner.setter
    def winner(self, w):
        self._winner = w

    @property
    def terminated(self):
        if self.atom:
            return (self.winner is not None)

        if self.winner is not None:
            return True

        return all(tile.terminated for tile in chain(*self.tiles))


class Game:
    def __init__(self, players, depth=3):
        self.players = cycle(players)
        self.root_level = Level(depth)
        self.choice_queue = deque(maxlen=depth-1)

    def get_head_level(self):
        level = self.root_level
        i = None
        for i, choice in enumerate(self.choice_queue):
            if level.terminated:
                break

            level = level[choice]

        return i, level

    def push_choice(self, choice):
        i, level = self.get_head_level()
        if level.terminated:
            self.choice_queue[i] = choice
            return

        self.choice_queue.append(choice)
        if level[choice].atom:
            level[choice].winner = next(self.players)