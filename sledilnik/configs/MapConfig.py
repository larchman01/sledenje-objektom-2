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
            self.fields[field] = {
                "topLeft": {
                    "x": self.fieldCorners[index][0],
                    "y": self.fieldCorners[index][1]
                },
                "topRight": {
                    "x": self.fieldCorners[index + 1][0],
                    "y": self.fieldCorners[index + 1][1]
                },
                "bottomLeft": {
                    "x": self.fieldCorners[index + 2][0],
                    "y": self.fieldCorners[index + 2][1]
                },
                "bottomRight": {
                    "x": self.fieldCorners[index + 3][0],
                    "y": self.fieldCorners[index + 3][1]
                }
            }
