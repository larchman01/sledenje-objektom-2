#!/usr/bin/env python
"""Main tracker Script"""
import getopt
from multiprocessing import Queue
import sys
import cv2.aruco as aruco
from VideoStreamer import VideoStreamer

from TrackerUtils import *
from Resources import *

debug = False


def startTracker(queue):
    # Load video
    cap = VideoStreamer()
    # cap.start(0)
    cap.start(ResFileNames.videoSource)

    # Setting up aruco tags
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)

    # Set aruco detector parameters
    arucoParameters = aruco.DetectorParameters_create()
    initArucoParameters(arucoParameters)

    # Initialize tracker stat variables
    configMap, quit, objects, frameCounter, gameData = initState()

    # Create window
    cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(ResGUIText.sWindowName, 2000,1000)

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

            queue.put(gameData)

            cv2.waitKey(1)

            if debug:
                # Draw GUI and objects
                frame = aruco.drawDetectedMarkers(frame, cornersTracked, ids)
                # Show frame
                cv2.imshow(ResGUIText.sWindowName, frame)

        else:
            break

    # When everything done, release the capture
    cv2.destroyAllWindows()
    sys.exit(0)


def main(argv):

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
            ResFileNames.videoSource = 0
            print("Set video source to: " + str(ResFileNames.videoSource))
        elif opt in ("-s", "--videoSource"):
            ResFileNames.videoSource = arg
            print("Set video source to: " + str(ResFileNames.videoSource))
        elif opt in ("-d", "--debug"):
            global debug
            debug = True


def helpText():
    print("usage:")
    print("\t-s <videoSource>            sets video source")
    print("\t--videoSource <videoSource> sets video source")
    print("\t-c                          sets camera as video source")
    print("\t--camera                    sets camera as video source")
    print("\t-d                          turns on debug mode")
    print("\t--debug                     turns on debug mode")


if __name__ == '__main__':
    main(sys.argv[1:])
    startTracker(Queue())
