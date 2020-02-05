from sledilnik.classes.Field import Field
from sledilnik.classes.Point import Point


class MapConfig:
    """Stores Map configs"""

    def __init__(self):
        self.fieldCorners = []
        self.fields = {}
        self.imageWidth = 0
        self.imageHeighth = 0
        self.fieldCornersVirtual = [[0, 200], [300, 200], [300, 0], [0, 0]]
        self.M = []

    def parseFields(self, fields):
        for i, field in enumerate(fields):
            index = i * 4
            self.fields[field] = Field(
                Point(self.fieldCorners[index][0], self.fieldCorners[index][1]),
                Point(self.fieldCorners[index + 1][0], self.fieldCorners[index + 1][1]),
                Point(self.fieldCorners[index + 2][0], self.fieldCorners[index + 2][1]),
                Point(self.fieldCorners[index + 3][0], self.fieldCorners[index + 3][1]),
            )
