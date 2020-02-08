from sledilnik.classes.Point import Point


class MovableObject:
    def __init__(self, x, y, dir):
        self.pos = Point(x, y)
        self.direction = dir

    def reprJSON(self):
        return {
            "x": self.pos.x,
            "y": self.pos.y,
            "dir": self.direction
        }
