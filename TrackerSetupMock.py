from sledilnik.TrackerSetup import TrackerSetup

trackerSetup = TrackerSetup()
trackerSetup.fileNamesConfig.videoSource = 'http://192.168.1.117/mjpg/video.mjpg'
trackerSetup.start()
