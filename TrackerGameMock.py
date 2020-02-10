from sledilnik.TrackerGame import TrackerGame

trackerGame = TrackerGame()
trackerGame.fileNamesConfig.videoSource = 'http://192.168.1.117/mjpg/video.mjpg'
trackerGame.debug = True
trackerGame.start()
