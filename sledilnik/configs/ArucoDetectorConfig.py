class ArucoDetectorConfig:
    def __init__(self):
        # Min.  okno za binarizacijo.  Premajhno okno naredi celotne tage iste
        # barve
        self.adaptiveThreshWinSizeMin = 10
        # Max.  okno.  Preveliko okno prevec zaokrozi kote bitov na tagu
        self.adaptiveThreshWinSizeMax = 23
        # Dno za thresholding.  Prenizko dno povzroci prevec kandidatov, previsoko
        # popaci tage (verjetno tudi odvisno od kontrasta)
        self.adaptiveThreshConstant = 7
        # Najmanjsa velikost kandidatov za tage.  Prenizko pregleda prevec
        # kandidatov in vpliva na performanse
        self.minMarkerPerimeterRate = 0.04
        # Najvecja velikost kandidatov.  Rahlo vpliva na performanse, vendar je
        # prevelikih kandidatov ponavadi malo
        self.maxMarkerPerimeterRate = 0.1
        # Algoritem izreze tag in ga upsampla na x pixlov na celico.  Vpliva na
        # prefromanse
        self.perspectiveRemovePixelPerCell = 30
        # Algoritem vsako celico obreze in gleda samo sredino.  Vecji faktor bolj
        # obreze
        self.perspectiveRemoveIgnoredMarginPerCell = 0.30
        # Verjetno najpomembnejsi parameter za nas.  Omejitev kako blizu sta lahko
        # dva taga.  Ker so nasi lahko zelo blizu,
        # moramo to nastaviti nizko, kar pa lahko pomeni, da isti tag detektira
        # dvakrat, kar lahko filtriramo naknadno.
        self.minMarkerDistanceRate = 0.001
