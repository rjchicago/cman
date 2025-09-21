"""Game entities: Cman and Ghost classes."""
from config import LIVES_START, HOME_TIME

class Cman:
    def __init__(self, start_pos, score=0, lives=None):
        sx, sy = start_pos
        self.x = float(sx)
        self.y = float(sy)
        self.dx = 0
        self.dy = 0
        self.want = (0, 0)
        self.lives = lives if lives is not None else LIVES_START
        self.power = 0.0
        self.shield = 1.0
        self.score = score

    def reset(self, start_pos):
        sx, sy = start_pos
        self.x = float(sx)
        self.y = float(sy)
        self.dx = 0
        self.dy = 0
        self.want = (0, 0)
        self.power = 0.0
        self.shield = 1.0

class Ghost:
    def __init__(self, home_pos, scatter):
        hx, hy = home_pos
        self.home = (hx, hy)
        self.x = float(hx)
        self.y = float(hy)
        self.dx = 0
        self.dy = 0
        self.scatter = scatter
        self.frightened = 0.0
        self.home_timer = 0.0

    def reset(self):
        self.x, self.y = float(self.home[0]), float(self.home[1])
        self.dx = self.dy = 0
        self.frightened = 0.0
        self.home_timer = HOME_TIME