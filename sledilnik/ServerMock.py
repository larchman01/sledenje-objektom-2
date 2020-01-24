from multiprocessing import Process, Queue, freeze_support

from sledilnik.Tracker import Tracker

if __name__ == '__main__':
    freeze_support()
    queue = Queue()

    tracker = Tracker()
    tracker.setVideoSource('ROBO_3.mp4')
    tracker.setDebug()

    p = Process(target=tracker.start, args=(queue,))
    p.start()

    for _ in range(100):
        gameData = queue.get()
        print(gameData)
