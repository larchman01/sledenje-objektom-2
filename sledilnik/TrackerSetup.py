import getopt
import json
import os
import pickle
import sys
from timeit import default_timer as timer

import cv2
import numpy as np

from .Resources import ResGUIText, ResKeys
from .Tracker import Tracker
from .classes.VideoStreamer import VideoStreamer
from .configs.MapConfig import MapConfig


class TrackerSetup(Tracker):
    def __init__(self):
        super().__init__()

        with open(self.fileNamesConfig.fieldsFilePath, "r") as output:
            self.fields = json.load(output)

        self.sFieldDefineGuide = []
        for field in self.fields:
            self.sFieldDefineGuide.extend(self.createText(field))
        self.sFieldDefineGuide.append(self.sFieldDefineGuide[0])

        self.fieldDefineGuideId = 0
        self.numOfCorners = len(self.fields) * 4

    def initState(self):
        quit = False
        configMap = MapConfig()
        if os.path.isfile(self.fileNamesConfig.mapConfigFilePath):
            configMap = pickle.load(open(self.fileNamesConfig.mapConfigFilePath, "rb"))
        frameCounter = 0

        return configMap, quit, frameCounter

    @staticmethod
    def putTextCentered(img, text, pos, font, fontScale, color, thickness=None, lineType=None):
        textsize = cv2.getTextSize(text, font, 1, 2)[0]
        textX = (pos[0] - textsize[0] // 2)
        cv2.putText(img, text, (textX, pos[1]), font, fontScale, color, thickness, lineType)

    def drawOverlay(self, frame, configMap, fieldEditMode):
        # Set font
        font = cv2.FONT_HERSHEY_SIMPLEX

        for i in range(len(configMap.fieldCorners)):
            cv2.circle(frame, tuple(configMap.fieldCorners[i]), 3, (0, 255, 255), 3)
            if i % 4 == 3:
                cv2.line(frame, tuple(configMap.fieldCorners[i - 1]), tuple(configMap.fieldCorners[i]), (0, 255, 255),
                         2)
                cv2.line(frame, tuple(configMap.fieldCorners[i - 3]), tuple(configMap.fieldCorners[i]), (0, 255, 255),
                         2)
            elif i > 0 and i % 4 != 0:
                cv2.line(frame, tuple(configMap.fieldCorners[i - 1]), tuple(configMap.fieldCorners[i]), (0, 255, 255),
                         2)

        # Display info when in map edit mode
        if fieldEditMode:
            self.putTextCentered(frame, self.sFieldDefineGuide[self.fieldDefineGuideId],
                                 (configMap.imageWidth // 2, 30), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Display help
        cv2.putText(frame, ResGUIText.sHelp, (10, configMap.imageHeight - 10), font, 0.5, (0, 0, 255), 1,
                    cv2.LINE_AA)

    @staticmethod
    def drawFPS(img, fps):
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Display FPS
        cv2.putText(img, ResGUIText.sFps + str(int(fps)), (10, 30), font, 1, (0, 255, 255), 2, cv2.LINE_AA)

    def getClickPoint(self, event, x, y, flags, param):
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
            self.fieldDefineGuideId += 1

            if len(configMap.fieldCorners) == self.numOfCorners:
                src = np.array([configMap.fieldCorners[0], configMap.fieldCorners[1], configMap.fieldCorners[2],
                                configMap.fieldCorners[3]],
                               np.float32)
                dst = np.array(configMap.fieldCornersVirtual, np.float32)
                configMap.M = cv2.getPerspectiveTransform(src, dst)

    def processKeys(self, configMap: MapConfig, fieldEditMode, quit):
        # Detect key press
        keypressed = cv2.waitKey(1) & 0xFF

        # Edit Map mode
        if keypressed == ord(ResKeys.editMapKey):
            fieldEditMode = not fieldEditMode
            if fieldEditMode:
                configMap.fieldCorners.clear()
                configMap.fields.clear()
                ResGUIText.fieldDefineGuideId = 0
                cv2.setMouseCallback(ResGUIText.sWindowName, self.getClickPoint, configMap)

        # Quit
        elif keypressed == ord(ResKeys.quitKey):
            quit = True

        return configMap, fieldEditMode, quit

    @staticmethod
    def createText(name):
        return ['Mark ' + name + ' Top Left Corner',
                'Mark ' + name + ' Field Top Right Corner',
                'Mark ' + name + ' Field Bottom Right Corner',
                'Mark ' + name + ' Field Bottom Left Corner']

    def start(self):
        # Load video
        cap = VideoStreamer()
        cap.start(self.fileNamesConfig.videoSource)

        # Initialize trackerSetup stat variables
        configMap, quit, frameCounter = self.initState()
        fieldEditMode = False

        # Create window
        cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)

        ts = timer()
        while not quit:

            # Load frame-by-frame
            if cap.running:
                frame = cap.read()

                if frame is None:
                    break

                # Convert to grayscale for Aruco detection
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frameCounter = frameCounter + 1

                frame = self.undistort(frame)
                configMap.imageHeight, configMap.imageWidth = frame.shape
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                # Dump latest map into file
                if fieldEditMode:
                    if len(configMap.fieldCorners) == self.numOfCorners:
                        configMap.parseFields(self.fields)

                        with open(self.fileNamesConfig.mapConfigFilePath, 'wb') as output:
                            pickle.dump(configMap, output, pickle.HIGHEST_PROTOCOL)
                            print(configMap.fields)

                        fieldEditMode = not fieldEditMode
                        cv2.setMouseCallback(ResGUIText.sWindowName, lambda *args: None)

                # Draw GUI and objects
                self.drawOverlay(frame, configMap, fieldEditMode)

                # Process keys
                (configMap, fieldEditMode, quit) = self.processKeys(configMap, fieldEditMode, quit)

                # Computer and display FPS
                te = timer()
                fps = 1 / (te - ts)
                self.drawFPS(frame, fps)
                ts = te

                # Show frame
                cv2.imshow(ResGUIText.sWindowName, frame)

        cv2.destroyAllWindows()
        sys.exit(0)


def main(argv, trackerSetup: TrackerSetup):
    try:
        opts, args = getopt.getopt(argv, "hs:c", ["videoSource="])
    except getopt.GetoptError:
        helpText()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpText()
            sys.exit()
        elif opt in ("-c", "--camera"):
            trackerSetup.fileNamesConfig.videoSource = 0
            print("Set video source to: " + str(0))
        elif opt in ("-s", "--videoSource"):
            trackerSetup.fileNamesConfig.videoSource = arg
            print("Set video source to: " + str(arg))


def helpText():
    print("usage:")
    print("\t-s <videoSource>            sets video source")
    print("\t--videoSource <videoSource> sets video source")
    print("\t-c                          sets camera as video source")
    print("\t--camera                    sets camera as video source")


if __name__ == '__main__':
    trackerSetup = TrackerSetup()
    main(sys.argv[1:], trackerSetup)
    trackerSetup.start()
