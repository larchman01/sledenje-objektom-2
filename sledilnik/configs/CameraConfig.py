class CameraConfig:
    def __init__(self):
        # Camera parameters for removing distortion
        self.k1 = -0.4077
        self.k2 = 0.2827
        self.k3 = -0.1436
        self.p1 = 6.6668e-4
        self.p2 = -0.0025
        self.fx = 1443  # 1.509369848235880e+03#
        self.fy = 1.509243126646947e+03
        self.cx = 9.678725207348843e+02
        self.cy = 5.356599023732050e+02

        # Scaling factors
        self.scale0 = 0.954
        self.scale1 = 0.00001
