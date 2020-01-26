import ujson


class ResFileNames:
    """Stores file names for json data"""
    gameDataFileName = "gameData.json"
    gameLiveDataFileName = "../nginx/html/game.json"
    mapConfigFilePath = "./mapConfig"
    fieldsFilePath = "./fields.json"
    videoSource = "http://192.168.0.2/mjpg/video.mjpg"


class ResKeys:
    editMapKey = 'e'
    quitKey = 'q'


def createText(name):
    return ['Mark ' + name + ' Top Left Corner',
            'Mark ' + name + ' Field Top Right Corner',
            'Mark ' + name + ' Field Bottom Right Corner',
            'Mark ' + name + ' Field Bottom Left Corner']


class ResGUIText:
    """Holds various strings displayed on window"""

    with open(ResFileNames.fieldsFilePath, "r") as output:
        fields = ujson.load(output)
    numOfCorners = len(fields) * 4
    sFieldDefineGuide = []
    for field in fields:
        sFieldDefineGuide.extend(createText(field))
    sFieldDefineGuide.append(sFieldDefineGuide[0])
    fieldDefineGuideId = 0

    sFps = 'FPS: '
    sTimeLeft = 'Time left: '
    sScore = ' Score: '
    sHelp = 'HotKeys: ' + ResKeys.editMapKey + ' - edit map | ' + ResKeys.quitKey + ' - quit'
    sWindowName = 'tracker'


class ResArucoDetector:
    # Min.  okno za binarizacijo.  Premajhno okno naredi celotne tage iste
    # barve
    adaptiveThreshWinSizeMin = 13
    # Max.  okno.  Preveliko okno prevec zaokrozi kote bitov na tagu
    adaptiveThreshWinSizeMax = 23
    # Dno za thresholding.  Prenizko dno povzroci prevec kandidatov, previsoko
    # popaci tage (verjetno tudi odvisno od kontrasta)
    adaptiveThreshConstant = 7
    # Najmanjsa velikost kandidatov za tage.  Prenizko pregleda prevec
    # kandidatov in vpliva na performanse
    minMarkerPerimeterRate = 0.04
    # Najvecja velikost kandidatov.  Rahlo vpliva na performanse, vendar je
    # prevelikih kandidatov ponavadi malo
    maxMarkerPerimeterRate = 0.1
    # Algoritem izreze tag in ga upsampla na x pixlov na celico.  Vpliva na
    # prefromanse
    perspectiveRemovePixelPerCell = 30
    # Algoritem vsako celico obreze in gleda samo sredino.  Vecji faktor bolj
    # obreze
    perspectiveRemoveIgnoredMarginPerCell = 0.30
    # Verjetno najpomembnejsi parameter za nas.  Omejitev kako blizu sta lahko
    # dva taga.  Ker so nasi lahko zelo blizu,
    # moramo to nastaviti nizko, kar pa lahko pomeni, da isti tag detektira
    # dvakrat, kar lahko filtriramo naknadno.
    minMarkerDistanceRate = 0.001


class ResCamera:
    """Stores camera configs"""

    # Camera parameters for removing distortion
    k1 = -0.4077
    k2 = 0.2827
    k3 = -0.1436
    p1 = 6.6668e-4
    p2 = -0.0025
    fx = 1445  # 1.509369848235880e+03#
    fy = 1.509243126646947e+03
    cx = 9.678725207348843e+02
    cy = 5.356599023732050e+02

    # Scaling factors
    scale0 = 0.954
    scale1 = 0.00001


class ResMap:
    """Stores Map configs"""

    def __init__(self):
        self.fieldCorners = []
        self.fields = {}
        self.imageWidth = 0
        self.imageHeighth = 0
        self.fieldCornersVirtual = [[0, 200], [300, 200], [300, 0], [0, 0]]
        self.M = []


class MovableObject:
    def __init__(self, id, x, y, dir):
        self.id = id
        self.x = x
        self.y = y
        self.direction = dir

    def reprJSON(self):
        return dict(id=self.id, x=self.x, y=self.y, dir=self.direction)


class GameLiveData:
    def __init__(self, configMap):
        self.fields = configMap.fields
        self.objects = {}

    def write(self, objects):
        self.objects.clear()
        for id, obj in objects.items():
            self.objects[id] = MovableObject(id, obj.position[0], obj.position[1], obj.direction)

    def reprJSON(self):
        return dict(fields=self.fields, objects=self.objects)


class ResKalmanFilter:
    """Stores Kalman Filter configs"""
    dt = 1  # Sampling rate
    u = 0.0  # Acceleration magnitude
    accNoiseMag = 0.003
    measurementNoiseX = 0.6
    measurementNoiseY = 0.6


class ResObjects:
    """Stores Object configs"""
    ObjectTimeout = 50
    PosLimitX = [-50, 3600]
    PosLimitY = [-50, 2100]
