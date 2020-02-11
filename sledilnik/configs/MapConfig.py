import cv2
import numpy as np

from sledilnik.classes.Field import Field
from sledilnik.classes.Point import Point


class MapConfig:
    """Stores Map configs"""

    def __init__(self):
        self.fieldCorners = []
        self.fields = {}
        self.imageWidth = 0
        self.imageHeighth = 0
        self.fieldCornersVirtual = [[0, 2055], [3555, 2055], [3555, 0], [0, 0]]
        self.M = []

    def parseFields(self, fields):
        for i, field in enumerate(fields):
            index = i * 4
            self.fields[field] = Field(
                Point(*self.moveOrigin(self.fieldCorners[index][0], self.fieldCorners[index][1], self)),
                Point(*self.moveOrigin(self.fieldCorners[index + 1][0], self.fieldCorners[index + 1][1], self)),
                Point(*self.moveOrigin(self.fieldCorners[index + 2][0], self.fieldCorners[index + 2][1], self)),
                Point(*self.moveOrigin(self.fieldCorners[index + 3][0], self.fieldCorners[index + 3][1], self)),
            )


    @staticmethod
    def moveOrigin(x, y, map):
        """Translates coordinate to new coordinate system and applies scaling to get units in ~mm.
        Args:
            x (int): x coordinate
            y (int): y coordinateq
            map (ResMap) : map object
        Returns:
            Tuple[int, int]: Corrected coordinates
        """
        # Translate coordinates if new origin exists (top left corner of map)
        # if len(map.fieldCorners) == 12:
        sPoint = np.array([np.array([[x, y]], np.float32)])
        dPoint = cv2.perspectiveTransform(sPoint, map.M)
        x = dPoint[0][0][0]
        y = dPoint[0][0][1]
        return int(round(x)), int(round(y))
