#!/usr/bin/env python
"""Main tracker Script"""
import getopt
import sys
from multiprocessing import Queue

import cv2
import cv2.aruco as aruco

from sledilnik.Resources import ResFileNames, ResGUIText
from sledilnik.TrackerUtils import initArucoParameters, initState, undistort, getMassCenter, track
from sledilnik.VideoStreamer import VideoStreamer


class Tracker:
    def __init__(self):
        self.__debug = False
        self.__videoSource = ResFileNames.videoSource

    def setDebug(self):
        self.__debug = not self.__debug

    def setVideoSource(self, videoSource):
        self.__videoSource = videoSource

    def start(self, queue=Queue()):
        # Load video
        cap = VideoStreamer()
        cap.start(self.__videoSource)

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

                if frame is None:
                    # while not queue.empty():
                    #     try:
                    #         queue.get(timeout=0.001)
                    #     except:
                    #         pass
                    # queue.close()
                    break

                # if ret:
                # Convert to grayscale for Aruco detection
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frameCounter = frameCounter + 1

                # Undistort image
                frame = undistort(frame)
                configMap.imageHeight, configMap.imageWidth = frame.shape
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                # Detect markers
                cornersTracked, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict,
                                                                             parameters=arucoParameters)

                # Compute mass centers and orientation
                pointsTracked = getMassCenter(cornersTracked, ids, configMap)

                # Detect Validate and track objects on map
                track(pointsTracked, objects, frameCounter)

                # Write game data to file
                gameData.write(objects)

                queue.put(gameData)

                cv2.waitKey(1)

                if self.__debug:
                    # Draw GUI and objects
                    frame = aruco.drawDetectedMarkers(frame, cornersTracked, ids)
                    # Show frame
                    cv2.imshow(ResGUIText.sWindowName, frame)

            else:
                break

        # When everything done, release the capture
        cv2.destroyAllWindows()
        sys.exit(0)


def main(argv, tracker: Tracker):
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
            tracker.setVideoSource(0)
            print("Set video source to: 0")
        elif opt in ("-s", "--videoSource"):
            tracker.setVideoSource(arg)
            print("Set video source to: " + str(arg))
        elif opt in ("-d", "--debug"):
            tracker.setDebug()


def helpText():
    print("usage:")
    print("\t-s <videoSource>            sets video source")
    print("\t--videoSource <videoSource> sets video source")
    print("\t-c                          sets camera as video source")
    print("\t--camera                    sets camera as video source")
    print("\t-d                          turns on debug mode")
    print("\t--debug                     turns on debug mode")


if __name__ == '__main__':
    tracker = Tracker()
    main(sys.argv[1:], tracker)
    tracker.start(Queue())
