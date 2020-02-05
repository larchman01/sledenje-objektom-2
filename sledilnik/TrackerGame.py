#!/usr/bin/env python
"""Main tracker Script"""
import getopt
import os
import pickle
import sys
from multiprocessing import Queue

import cv2
import cv2.aruco as aruco
import numpy as np

from .Resources import ResGUIText, ResKeys
from .Tracker import Tracker
from .classes.ObjectTracker import ObjectTracker
from .classes.TrackerLiveData import TrackerLiveData
from .classes.VideoStreamer import VideoStreamer
from .configs.MapConfig import MapConfig


class TrackerGame(Tracker):
    def __init__(self):
        super().__init__()
        self.debug = False

    def initState(self):
        quit = False
        configMap = MapConfig()
        if os.path.isfile(self.fileNamesConfig.mapConfigFilePath):
            configMap = pickle.load(open(self.fileNamesConfig.mapConfigFilePath, "rb"))
        else:
            print("Can't open map configurations!")
            quit = True
        frameCounter = 0
        gameData = TrackerLiveData(configMap)

        return configMap, quit, frameCounter, gameData

    def track(self, pointsTracked, objects, frame_counter):
        for ct in pointsTracked:
            id = ct[0]
            position = ct[1]
            if id in objects:
                objects[id].updateState(position)
                objects[id].detected = True
                objects[id].enabled = True
                objects[id].last_seen = frame_counter
            else:
                objects[id] = ObjectTracker(id, position, (0, 0, 0, 0), self.kalmanFilterConfig)

        # Disable object tracking if not  detected for a long time
        for k, v in list(objects.items()):
            if ((frame_counter - v.last_seen) > self.objectsConfig.objectTimeout) or not self.isValidPos(
                    v.position[0:2]):
                del objects[k]
                # objects[k].enabled = False

        # Track undetected objects
        for obj in objects:
            if not objects[obj].detected:
                objects[obj].lost_frames = objects[obj].lost_frames + 1
                # if objects[obj].enabled == True:
                objects[obj].updateState([])
            objects[obj].detected = False

    def initArucoParameters(self, arucoParameters):
        arucoParameters.adaptiveThreshWinSizeMin = self.arucoDetectorConfig.adaptiveThreshWinSizeMin
        arucoParameters.adaptiveThreshWinSizeMax = self.arucoDetectorConfig.adaptiveThreshWinSizeMax
        arucoParameters.adaptiveThreshConstant = self.arucoDetectorConfig.adaptiveThreshConstant
        arucoParameters.minMarkerPerimeterRate = self.arucoDetectorConfig.minMarkerPerimeterRate
        arucoParameters.maxMarkerPerimeterRate = self.arucoDetectorConfig.maxMarkerPerimeterRate
        arucoParameters.perspectiveRemovePixelPerCell = self.arucoDetectorConfig.perspectiveRemovePixelPerCell
        arucoParameters.perspectiveRemoveIgnoredMarginPerCell = self.arucoDetectorConfig.perspectiveRemoveIgnoredMarginPerCell
        arucoParameters.minMarkerDistanceRate = self.arucoDetectorConfig.minMarkerDistanceRate

    def correct(self, x, y, map):
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
        scale0 = self.cameraConfig.scale0
        scale1 = self.cameraConfig.scale1

        # Convert screen coordinates to 0-based coordinates
        offset_x = map.imageWidth / 2
        offset_y = map.imageHeighth / 2

        # Calculate distance from center
        dist = np.sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)

        # Correct coordinates and return
        return (int(round((x - offset_x) * (scale0 + scale1 * dist) + offset_x)),
                int(round((y - offset_y) * (scale0 + scale1 * dist) + offset_y)))
        # return(x,y)

    def getMassCenter(self, corners, ids, map):
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
            (Cx, Cy) = self.moveOrigin(*self.correct((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, map), map)
            (CxTop, CyTop) = self.moveOrigin(*self.correct((x1 + x2) / 2, (y1 + y2) / 2, map), map)
            massCenters.append([ids[id][0], (Cx, Cy, CxTop, CyTop)])
            id = id + 1
        return massCenters

    def isValidPos(self, pos):
        if self.objectsConfig.posLimitX[0] <= pos[0] <= self.objectsConfig.posLimitX[1] and \
                self.objectsConfig.posLimitY[0] <= pos[1] <= \
                self.objectsConfig.posLimitY[1]:
            return True
        return False

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
        if len(map.fieldCorners) == 12:
            sPoint = np.array([np.array([[x, y]], np.float32)])
            dPoint = cv2.perspectiveTransform(sPoint, map.M)
            x = dPoint[0][0][0]
            y = dPoint[0][0][1]
        return int(round(x)), int(round(y))

    @staticmethod
    def processKeys():
        # Detect key press
        keypressed = cv2.waitKey(1) & 0xFF
        return keypressed == ord(ResKeys.quitKey)

    def start(self, queue=Queue()):
        # Load video
        cap = VideoStreamer()
        cap.start(self.fileNamesConfig.videoSource)

        # Setting up aruco tags
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)

        # Set aruco detector parameters
        arucoParameters = aruco.DetectorParameters_create()
        self.initArucoParameters(arucoParameters)

        # Initialize tracker stat variables
        configMap, quit, frameCounter, gameData = self.initState()
        objects = dict()

        # Create window
        cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(ResGUIText.sWindowName, 2000,1000)

        while not quit:

            # Load frame-by-frame
            if cap.running:
                frame = cap.read()

                if frame is None:
                    break

                # Convert to grayscale for Aruco detection
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frameCounter = frameCounter + 1

                # Undistort image
                frame = self.undistort(frame)
                configMap.imageHeight, configMap.imageWidth = frame.shape
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                # Detect markers
                cornersTracked, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict,
                                                                             parameters=arucoParameters)

                # Compute mass centers and orientation
                pointsTracked = self.getMassCenter(cornersTracked, ids, configMap)

                # Detect Validate and track objects on map
                self.track(pointsTracked, objects, frameCounter)

                # Write game data to file
                gameData.write(objects)

                queue.put(gameData)

                quit = self.processKeys()

                if self.debug:
                    # Draw GUI and objects
                    frame = aruco.drawDetectedMarkers(frame, cornersTracked, ids)
                    # Show frame
                    cv2.imshow(ResGUIText.sWindowName, frame)

            else:
                break

        # When everything done, release the capture
        cv2.destroyAllWindows()
        sys.exit(0)


def main(argv, tracker: TrackerGame):
    try:
        opts, args = getopt.getopt(argv, "hs:cd", ["videoSource="])
    except getopt.GetoptError:
        helpText()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpText()
            sys.exit()
        elif opt in ("-c", "--camera"):
            tracker.fileNamesConfig.videoSource = 0
            print("Set video source to: 0")
        elif opt in ("-s", "--videoSource"):
            tracker.fileNamesConfig.videoSource = arg
            print("Set video source to: " + str(arg))
        elif opt in ("-d", "--debug"):
            tracker.debug = True


def helpText():
    print("usage:")
    print("\t-s <videoSource>            sets video source")
    print("\t--videoSource <videoSource> sets video source")
    print("\t-c                          sets camera as video source")
    print("\t--camera                    sets camera as video source")
    print("\t-d                          turns on debug mode")
    print("\t--debug                     turns on debug mode")


if __name__ == '__main__':
    tracker = TrackerGame()
    main(sys.argv[1:], tracker)
    tracker.start(Queue())
