from sledilnik.classes.Point import Point


class MovableObject:
    def __init__(self, id: int, x, y, dir):
        self.id = id
        self.pos = Point(x, y)
        self.direction = dir

    def reprJSON(self):
        return {
            "id": self.id,
            "x": self.pos.x,
            "y": self.pos.y,
            "dir": self.direction
        }
