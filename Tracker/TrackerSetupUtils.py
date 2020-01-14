import cv2
import numpy as np
# from Resources import *

from Tracker.Resources import ResCamera, ResGUIText, ResKeys, ResMap


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


def getClickPoint(event, x, y, flags, param):
    """Callback function used in handling click events when defining the map.
    Args:
        event (int): type of event
        x (int): event position x
        y (int): event position y
        flags: event flags
        param:
    Returns:
        bool: True if object in area
    """
    configMap = param
    if event == cv2.EVENT_LBUTTONDOWN:

        configMap.fieldCorners.append([x, y])
        ResGUIText.fieldDefineGuideId += 1

        if len(configMap.fieldCorners) == ResGUIText.numOfCorners:
            src = np.array([configMap.fieldCorners[0], configMap.fieldCorners[1], configMap.fieldCorners[2],
                            configMap.fieldCorners[3]],
                           np.float32)
            dst = np.array(configMap.fieldCornersVirtual, np.float32)
            configMap.M = cv2.getPerspectiveTransform(src, dst)


def putTextCentered(img, text, pos, font, fontScale, color, thickness=None, lineType=None):
    textsize = cv2.getTextSize(text, font, 1, 2)[0]
    textX = (pos[0] - textsize[0] // 2)
    cv2.putText(img, text, (textX, pos[1]), font, fontScale, color, thickness, lineType)


def drawOverlay(frame, configMap, fieldEditMode):
    # Set font
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(len(configMap.fieldCorners)):
        cv2.circle(frame, tuple(configMap.fieldCorners[i]), 3, (0, 255, 255), 3)
        if i % 4 == 3:
            cv2.line(frame, tuple(configMap.fieldCorners[i-1]), tuple(configMap.fieldCorners[i]), (0, 255, 255), 2)
            cv2.line(frame, tuple(configMap.fieldCorners[i-3]), tuple(configMap.fieldCorners[i]), (0, 255, 255), 2)
        elif i > 0 and i % 4 != 0:
            cv2.line(frame, tuple(configMap.fieldCorners[i-1]), tuple(configMap.fieldCorners[i]), (0, 255, 255), 2)

    # Display info when in map edit mode
    if fieldEditMode:
        putTextCentered(frame, ResGUIText.sFieldDefineGuide[ResGUIText.fieldDefineGuideId],
                        (configMap.imageWidth // 2, 30), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Display help
    cv2.putText(frame, ResGUIText.sHelp, (10, configMap.imageHeight - 10), font, 0.5, (0, 0, 255), 1,
                cv2.LINE_AA)


def drawFPS(img, fps):
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Display FPS
    cv2.putText(img, ResGUIText.sFps + str(int(fps)), (10, 30), font, 1, (0, 255, 255), 2, cv2.LINE_AA)


def processKeys(configMap: ResMap, fieldEditMode, quit):
    # Detect key press
    keypressed = cv2.waitKey(1) & 0xFF

    # Edit Map mode
    if keypressed == ord(ResKeys.editMapKey):
        fieldEditMode = not fieldEditMode
        if fieldEditMode:
            configMap.fieldCorners.clear()
            configMap.fields.clear()
            ResGUIText.fieldDefineGuideId = 0
            cv2.setMouseCallback(ResGUIText.sWindowName, getClickPoint, configMap)

    # Quit
    elif keypressed == ord(ResKeys.quitKey):
        quit = True

    return configMap, fieldEditMode, quit


def parseFields(configMap):
    for i, field in enumerate(ResGUIText.fields):
        index = i * 4
        configMap.fields[field] = {
            "topLeft": configMap.fieldCorners[index],
            "topRight": configMap.fieldCorners[index+1],
            "bottomLeft": configMap.fieldCorners[index+2],
            "bottomRight": configMap.fieldCorners[index+3]
        }