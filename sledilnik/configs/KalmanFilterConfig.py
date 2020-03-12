class KalmanFilterConfig:
    def __init__(self):
        # Sampling rate
        self.dt = 1
        # Acceleration magnitude
        self.u = 0.0
        self.accNoiseMag = 0.003
        self.measurementNoiseX = 0.6
        self.measurementNoiseY = 0.6
