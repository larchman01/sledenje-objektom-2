import pickle
import sys
import os

from timeit import default_timer as timer
from VideoStreamer import VideoStreamer
from TrackerSetupUtils import *
from Resources import *
from Resources import ResMap

# Load video
cap = VideoStreamer()
# cap.start(ResFileNames.videoSource)
# cap.start(0)
cap.start("./ROBO_3.mp4")

# Initialize trackerSetup stat variables
fieldEditMode = False
quit = False

configMap = ResMap()
if os.path.isfile(ResFileNames.mapConfigFilePath):
    configMap = pickle.load(open(ResFileNames.mapConfigFilePath, "rb"))

frameCounter = 0

# Create window
cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)


ts = timer()
while not quit:

    # Load frame-by-frame

    if cap.running:
        frame = cap.read()

        # Convert to grayscale for Aruco detection
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frameCounter = frameCounter + 1

        frame = undistort(frame)
        configMap.imageHeight, configMap.imageWidth = frame.shape
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Dump latest map into file
        if fieldEditMode:
            if len(configMap.fieldCorners) == ResGUIText.numOfCorners:

                parseFields(configMap)

                # os.remove(ResFileNames.mapConfigFilePath)
                # TODO delete old config
                with open(ResFileNames.mapConfigFilePath, 'wb') as output:
                    pickle.dump(configMap, output, pickle.HIGHEST_PROTOCOL)
                    print(configMap.fields)

                fieldEditMode = False

        # Draw GUI and objects
        drawOverlay(frame, configMap, fieldEditMode)

        # Process keys
        (configMap, fieldEditMode, quit) = processKeys(configMap, fieldEditMode, quit)

        # Computer and display FPS
        te = timer()
        fps = 1 / (te - ts)
        drawFPS(frame, fps)
        ts = te

        # Show frame
        cv2.imshow(ResGUIText.sWindowName, frame)

cv2.destroyAllWindows()
sys.exit(0)
