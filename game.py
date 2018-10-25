class Level:
    def __init__(self, depth=0):
        self.atom = (depth == 0)

        if not self.atom:
            self.tiles = [[Level(depth-1) for _ in range(3)] for _ in range(3)]

        self._winner = None

    def move(self, player, location_stack):
        if self.atom:
            self._winner = player
            return

        x, y = location_stack.pop()
        self.tiles[y][x].move(player, location_stack)

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
        if self._winner is not None or self.atom:
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

l = Level(1)
l.move(1, [(0, 0)])
l.move(1, [(0, 2)])
l.move(2, [(2, 0)])
l.move(2, [(1, 1)])
l.move(2, [(0, 2)])
print(l.winner)