import cv2
import numpy as np

from .configs.ArucoDetectorConfig import ArucoDetectorConfig
from .configs.CameraConfig import CameraConfig
from .configs.FileNamesConfig import FileNamesConfig
from .configs.KalmanFilterConfig import KalmanFilterConfig
from .configs.ObjectsConfig import ObjectsConfig


class Tracker:
    def __init__(self):
        self.arucoDetectorConfig = ArucoDetectorConfig()
        self.cameraConfig = CameraConfig()
        self.fileNamesConfig = FileNamesConfig()
        self.kalmanFilterConfig = KalmanFilterConfig()
        self.objectsConfig = ObjectsConfig()

    def undistort(self, img):
        # Camera parameters
        k1 = self.cameraConfig.k1
        k2 = self.cameraConfig.k2
        k3 = self.cameraConfig.k3
        p1 = self.cameraConfig.p1
        p2 = self.cameraConfig.p2
        fx = self.cameraConfig.fx
        fy = self.cameraConfig.fy
        cx = self.cameraConfig.cx
        cy = self.cameraConfig.cy
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

    # def reverseCorrect(self, x, y, map):
    #     """Reverses the correction of the coordinates.
    #     Scale0 and scale1 define scaling constants. The scaling factor is a linear function of distance from center.
    #     Args:
    #         x (int): x coordinate
    #         y (int): y coordinate
    #         map (ResMap) : map object
    #     Returns:
    #         Tuple[int, int]: Reverted coordinates
    #     """
    #
    #     # Scaling factors
    #     scale0 = self.cameraConfig.scale0
    #     scale1 = self.cameraConfig.scale1
    #
    #     # Convert screen coordinates to 0-based coordinates
    #     offset_x = map.imageWidth / 2
    #     offset_y = map.imageHeighth / 2
    #
    #     # Calculate distance from center
    #     dist = np.sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)
    #
    #     # Find the distance before correction
    #     distOld = (-scale0 + np.sqrt(scale0 ** 2 + 4 * dist * scale1)) / (2 * scale1)
    #
    #     # Revert coordinates and return
    #     return (int(round((x - offset_x) / (scale0 + scale1 * distOld) + offset_x)),
    #             int(round((y - offset_y) / (scale0 + scale1 * distOld) + offset_y)))
