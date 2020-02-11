from math import pi

from sledilnik.classes.Point import Point


class MovableObject:
    def __init__(self, id: int, x, y, dir):
        self.id = id
        self.pos = Point(x, y)
        self.direction = float(dir * 180 / pi)

    def reprJSON(self):
        return {
            "id": self.id,
            "position": self.pos.reprJSON(),
            "dir": self.direction
        }
