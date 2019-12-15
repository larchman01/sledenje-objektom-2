#!/usr/bin/env python
"""Main tracker Script"""

from timeit import default_timer as timer
import sys
import cv2.aruco as aruco
from VideoStreamer import VideoStreamer

from TrackerUtils import *
from Resources import *


def startTracker(queue):
    # Load video
    cap = VideoStreamer()
    # cap.start(0)
    cap.start("./ROBO_3.mp4")

    # Setting up aruco tags
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)

    # Set aruco detector parameters
    arucoParameters = aruco.DetectorParameters_create()
    initArucoParameters(arucoParameters)

    # Initialize tracker stat variables
    configMap, quit, objects, frameCounter, gameData = initState()

    # just for sorting gameData first Time
    # with open(ResFileNames.gameDataFileName, "w") as
    # f:
    #    ujson.dump(gameData,f)

    # Create window
    cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(ResGUIText.sWindowName, 2000,1000)

    # Start the FPS timer
    ts = timer()
    while not quit:

        # Load frame-by-frame

        # ret, frame = cap.read()
        if cap.running:
            frame = cap.read()

            # if ret:
            # Convert to grayscale for Aruco detection
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frameCounter = frameCounter + 1

            # Undistort image
            frame = undistort(frame)
            configMap.imageHeight, configMap.imageWidth = frame.shape
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # Detect markers
            cornersTracked, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=arucoParameters)

            # Compute mass centers and orientation
            pointsTracked = getMassCenter(cornersTracked, ids, configMap)

            # Detect Validate and track objects on map
            track(pointsTracked, objects, frameCounter)

            # Write game data to file
            gameData.write(objects)

            # TODO Writes to a multiprocess queue
            queue.put(gameData)

            # TODO
            cv2.waitKey(1)

            # Draw GUI and objects
            frame = aruco.drawDetectedMarkers(frame, cornersTracked, ids)
            # Show frame
            cv2.imshow(ResGUIText.sWindowName, frame)

            # print(gameData.objects)

        else:
            break

    # When everything done, release the capture
    # t.join()
    # cap.stop()
    cv2.destroyAllWindows()
    sys.exit(0)


if __name__ == '__main__':
    startTracker(0)
