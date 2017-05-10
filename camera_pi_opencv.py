import time
import io
import threading
import picamera
import pickle
import cv2
import numpy as np

class Camera_cv(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera_cv.thread is None:
            # start background frame thread
            Camera_cv.thread = threading.Thread(target=self._thread)
            Camera_cv.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera_cv.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                i = cv2.imdecode(np.fromstring(stream.read(), dtype=np.uint8), 1)
                pickled = pickle.dumps(i, protocol=0)
                cls.frame = pickled

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
