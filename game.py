from itertools import chain, cycle

class Level:
    def __init__(self, depth=0):
        self.atom = (depth == 0)

        if not self.atom:
            self.tiles = [[Level(depth-1) for _ in range(3)] for _ in range(3)]

        self._winner = None
        self._terminated = False

    def move(self, player, location_stack):
        if self.atom:
            self._winner = player
            self._terminated = True
            return

        x, y = location_stack.pop()
        self[x, y].move(player, location_stack)

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
        if self.atom or self._winner is not None:
            return self._winner

        lines = (
            *self.tiles,  # horizontal
            *zip(*self.tiles),  # vertical (transposed)
            (self.tiles[i][i] for i in range(3)),  # diagonals
            (self.tiles[i][2-i] for i in range(3)),
        )

        for line in lines:
            self._winner = self._winner or self.test_equals(line)

        if self._winner is not None:
            self._terminated = True

        return self._winner

    @property
    def terminated(self):
        if self.atom or self._terminated:
            return self._terminated

        self._terminated = all(tile.terminated for tile in chain(*self.tiles))
        return self._terminated
