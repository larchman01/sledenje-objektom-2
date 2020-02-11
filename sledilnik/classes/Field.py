from sledilnik.classes.Point import Point


class Field:
    def __init__(self, topLeft: Point, topRight: Point, bottomRight: Point, bottomLeft: Point):
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight

    def reprJSON(self):
        return {
            "topLeft": self.topLeft.reprJSON(),
            "topRight": self.topRight.reprJSON(),
            "bottomLeft": self.bottomLeft.reprJSON(),
            "bottomRight": self.bottomRight.reprJSON()
        }

    def reprTuple(self) -> tuple:
        return (
            self.topLeft.reprTuple(),
            self.topRight.reprTuple(),
            self.bottomLeft.reprTuple(),
            self.bottomRight.reprTuple()
        )
