import pyrealsense2 as rs
import numpy as np
import cv2 as cv
from threading import Thread, Lock
from time import sleep

class RealCam:

    def __init__(self, showVideo=False, pixel=(640, 480), frames=30):
        # initialization of camera
        self.frame = None
        self.imageDepth = None
        self.imageColor = None
        self.depthColormap = None
        self.lock = Lock()

        self.init_pipeline(pixel, frames)
        self.init_capture()

        if showVideo:
            self.show_video()

        print('Realsense Cam was initialized')

    def init_pipeline(self, pixel, frames):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_stream(rs.stream.depth, 
                pixel[0],
                pixel[1], 
                rs.format.z16, 
                frames)
        
        self.config.enable_stream(rs.stream.color, 
                pixel[0], 
                pixel[1],
                rs.format.bgr8, 
                frames)
        
        self.pipeline.start(self.config)
        
    def init_capture(self):
        def capture_frame_thread():
            try:
                while True:
                    self.lock.acquire()
                    self.frame = self.pipeline.wait_for_frames()
                    frameDepth = self.frame.get_depth_frame()
                    frameColor = self.frame.get_color_frame()

                    if not frameDepth or not frameColor:
                        pass

                    self.imageDepth = np.asarray(frameDepth.get_data())
                    self.imageColor = np.asarray(frameColor.get_data())
                    
                    self.depthColormap = cv.applyColorMap(cv.convertScaleAbs(self.imageDepth,
                        alpha=0.03), cv.COLORMAP_JET)
                    self.lock.release()
                    sleep(0.001)
            finally:
                self.pipeline.stop()

        self.capture_frame_thread = Thread(target=capture_frame_thread, args=())
        self.capture_frame_thread.daemon = True
        self.capture_frame_thread.start()

    def show_video(self):
        def show_video_thread():
            cv.namedWindow('Realsense', cv.WINDOW_AUTOSIZE)
        
            while True:
                self.lock.acquire()
                cv.imshow("Realsense", np.hstack((self.imageColor, self.depthColormap)))
                keyCode = cv.waitKey(1)
                self.lock.release()

        self.video_thread = Thread(target=show_video_thread, args=())
        self.video_thread.daemon = True
        self.video_thread.start()

    def get_frame(self):
        if self.imageColor is None or self.depthColormap is None:
            return None
        self.lock.acquire()
        frame = np.copy(self.imageColor) 
        depth = np.copy(self.depthColormap)
        self.lock.release()
        return np.hstack((frame, depth))
    
if __name__ == '__main__':
    realCam = RealCam(showVideo=True)
    while True:
        pass
