import os
import pickle
from math import sqrt

import cv2
import numpy as np

from Tracker.ObjectTracker import ObjectTracker
from Tracker.Resources import ResCamera, ResArucoDetector, ResFileNames, ResMap, ResGameLiveData, ResObjects, ResKeys


def undistort(img):
    # Camera parameters
    k1 = ResCamera.k1
    k2 = ResCamera.k2
    k3 = ResCamera.k3
    p1 = ResCamera.p1
    p2 = ResCamera.p2
    fx = ResCamera.fx
    fy = ResCamera.fy
    cx = ResCamera.cx
    cy = ResCamera.cy
    dist = np.array([k1, k2, p1, p2, k3])
    mtx = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    # Setting the params
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # Undistort
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
    dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    # Crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    return dst


def initArucoParameters(arucoParameters):
    arucoParameters.adaptiveThreshWinSizeMin = ResArucoDetector.adaptiveThreshWinSizeMin
    arucoParameters.adaptiveThreshWinSizeMax = ResArucoDetector.adaptiveThreshWinSizeMax
    arucoParameters.adaptiveThreshConstant = ResArucoDetector.adaptiveThreshConstant
    arucoParameters.minMarkerPerimeterRate = ResArucoDetector.minMarkerPerimeterRate
    arucoParameters.maxMarkerPerimeterRate = ResArucoDetector.maxMarkerPerimeterRate
    arucoParameters.perspectiveRemovePixelPerCell = ResArucoDetector.perspectiveRemovePixelPerCell
    arucoParameters.perspectiveRemoveIgnoredMarginPerCell = ResArucoDetector.perspectiveRemoveIgnoredMarginPerCell
    arucoParameters.minMarkerDistanceRate = ResArucoDetector.minMarkerDistanceRate


def initState():
    # gameData, configMap, quit, objects

    quit = False
    configMap = ResMap()
    if os.path.isfile(ResFileNames.mapConfigFilePath):
        configMap = pickle.load(open(ResFileNames.mapConfigFilePath, "rb"))
    else:
        print("Can't open map configurations!")
        quit = True
    objects = dict()
    frameCounter = 0
    gameData = ResGameLiveData(configMap)

    return configMap, quit, objects, frameCounter, gameData


def correct(x, y, map):
    """Corrects the coordinates.
    Scale0 and scale1 define scaling constants. The scaling factor is a linear function of distance from center.
    Args:
        x (int): x coordinate
        y (int): y coordinate
        map (ResMap) : map object
    Returns:
        Tuple[int, int]: Corrected coordinates
    """

    # Scaling factors
    scale0 = ResCamera.scale0
    scale1 = ResCamera.scale1

    # Convert screen coordinates to 0-based coordinates
    offset_x = map.imageWidth / 2
    offset_y = map.imageHeighth / 2

    # Calculate distance from center
    dist = sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)

    # Correct coordinates and return
    return (int(round((x - offset_x) * (scale0 + scale1 * dist) + offset_x)),
            int(round((y - offset_y) * (scale0 + scale1 * dist) + offset_y)))
    # return(x,y)


def reverseCorrect(x, y, map):
    """Reverses the correction of the coordinates.
    Scale0 and scale1 define scaling constants. The scaling factor is a linear function of distance from center.
    Args:
        x (int): x coordinate
        y (int): y coordinate
        map (ResMap) : map object
    Returns:
        Tuple[int, int]: Reverted coordinates
    """

    # Scaling factors
    scale0 = ResCamera.scale0
    scale1 = ResCamera.scale1

    # Convert screen coordinates to 0-based coordinates
    offset_x = map.imageWidth / 2
    offset_y = map.imageHeighth / 2

    # Calculate distance from center
    dist = sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)

    # Find the distance before correction
    distOld = (-scale0 + sqrt(scale0 ** 2 + 4 * dist * scale1)) / (2 * scale1)

    # Revert coordinates and return
    return (int(round((x - offset_x) / (scale0 + scale1 * distOld) + offset_x)),
            int(round((y - offset_y) / (scale0 + scale1 * distOld) + offset_y)))


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
    if len(map.fieldCorners) == 12:
        sPoint = np.array([np.array([[x, y]], np.float32)])
        dPoint = cv2.perspectiveTransform(sPoint, map.M)
        x = dPoint[0][0][0]
        y = dPoint[0][0][1]
    return (int(round(x)), int(round(y)))


def getMassCenter(corners, ids, map):
    """Computes mass centers of objects in the frame.
    Args:
        corners (array of array of float): corners of each object in the frame
        ids (array of array of int): aruco tag ids
        map (ResMap) : map object
    Returns:
        List[int, Tuple[float, float, float, float]]: List of aruco tag ids with object center and top coordinates
    """
    id = 0
    massCenters = []
    for object in corners:
        x1 = object[0][0][0]
        y1 = object[0][0][1]
        x2 = object[0][1][0]
        y2 = object[0][1][1]
        x3 = object[0][2][0]
        y3 = object[0][2][1]
        x4 = object[0][3][0]
        y4 = object[0][3][1]

        # A=1/2*(x1*y2-x2*y1+x2*y3-x3*y2+x3*y4-x4*y3+x4*y1-x1*y4);
        # Cx=1/(6*A)*((x1+x2)*(x1*y2-x2*y1)+ \
        # (x2+x3)*(x2*y3-x3*y2)+ \
        # (x3+x4)*(x3*y4-x4*y3)+ \
        # (x4+x1)*(x4*y1-x1*y4))
        (Cx, Cy) = moveOrigin(*correct((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, map), map)
        (CxTop, CyTop) = moveOrigin(*correct((x1 + x2) / 2, (y1 + y2) / 2, map), map)
        massCenters.append([ids[id][0], (Cx, Cy, CxTop, CyTop)])
        id = id + 1
    return massCenters


def isValidPos(pos):
    if ResObjects.PosLimitX[0] <= pos[0] <= ResObjects.PosLimitX[1] and ResObjects.PosLimitY[0] <= pos[1] <= \
            ResObjects.PosLimitY[1]:
        return True
    return False


def track(pointsTracked, objects, frame_counter):
    for ct in pointsTracked:
        id = ct[0]
        position = ct[1]
        if id in objects:
            objects[id].updateState(position)
            objects[id].detected = True
            objects[id].enabled = True
            objects[id].last_seen = frame_counter
        # if object seen first time add it to the list of tracked objects
        # else:
        #     if id in ResObjects.RobotIds:
        #         objects[id] = ObjectTracker(ResObjects.ROBOT, id, position, (0, 0, 0, 0))
        #         objects[id].last_seen = frame_counter
        #     elif id in ResObjects.ApplesGoodIds:
        #         objects[id] = ObjectTracker(ResObjects.APPLE_GOOD, id, position, (0, 0, 0, 0))
        #         objects[id].last_seen = frame_counter
        #     elif id in ResObjects.ApplesBadIds:
        #         objects[id] = ObjectTracker(ResObjects.APPLE_BAD, id, position, (0, 0, 0, 0))
        #         objects[id].last_seen = frame_counter
        else:
            objects[id] = ObjectTracker(id, position, (0, 0, 0, 0))

    # Disable object tracking if not  detected for a long time
    for k, v in list(objects.items()):
        if ((frame_counter - v.last_seen) > ResObjects.ObjectTimeout) or not isValidPos(v.position[0:2]):
            del objects[k]
            # objects[k].enabled = False

    # Track undetected objects
    for obj in objects:
        if objects[obj].detected == False:
            objects[obj].lost_frames = objects[obj].lost_frames + 1
            # if objects[obj].enabled == True:
            objects[obj].updateState([])
        objects[obj].detected = False


def processKeys(configMap, fieldEditMode, quit):
    # Detect key press
    keypressed = cv2.waitKey(1) & 0xFF

    # Quit
    if keypressed == ord(ResKeys.quitKey):
        quit = True

    return configMap, fieldEditMode, quit


def writeGameData(configMap, objects):
    gameData = ResGameLiveData()
    gameData.fields = configMap.fields
    gameData.objects = {}
    return gameData
