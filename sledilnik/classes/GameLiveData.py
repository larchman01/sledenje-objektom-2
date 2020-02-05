from typing import Dict

from sledilnik.classes.MovableObject import MovableObject


class GameLiveData:
    def __init__(self, configMap):
        self.fields = configMap.fields
        self.objects: Dict[int, MovableObject] = {}

    def write(self, objects):
        self.objects.clear()
        for idObject, obj in objects.items():
            self.objects[idObject] = MovableObject(obj.position[0], obj.position[1], obj.direction)

    def reprJSON(self):
        return {
            "fields": self.fields,
            "objects": {str(objectId): mObject.reprJSON() for objectId, mObject in self.objects.items()}
        }
