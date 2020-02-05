class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def reprJSON(self):
        return {
            "x": self.x,
            "y": self.y,
        }
