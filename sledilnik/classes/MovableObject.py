class MovableObject:
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.direction = dir

    def reprJSON(self):
        return {
            "x": self.x,
            "y": self.y,
            "dir": self.direction
        }
