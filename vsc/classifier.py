import os
import zmq
import mss
import sys
import cv2
import json
import ctypes
import platform
import argparse
import numpy as np
from prefetch_generator import background


class Monitor():

    def __init__(self, mss, monitor_info=None):
        self.mss = mss
        self.monitor = self.mss.monitors[monitor_info['monitor_num']]
        self.w, self.h = monitor_info["source_size"]
        self.top, self.left, self.right, self.bottom = monitor_info["crop"]
        self._mss_bugfix()
        self._update_monitor()

    def _mss_bugfix(self):
        """Temporary windows DPI bugfix for mss"""

        os_ = platform.system().lower()
        if os_ == "windows":
            version = sys.getwindowsversion()[:2]
            if version >= (6, 3):
                # Windows 8.1+
                # Here 2 = PROCESS_PER_MONITOR_DPI_AWARE, which means:
                #     per monitor DPI aware. This app checks for the DPI when it is
                #     created and adjusts the scale factor whenever the DPI changes.
                #     These applications are not automatically scaled by the system.
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            elif (6, 0) <= version < (6, 3):
                # Windows Vista, 7, 8 and Server 2012
                ctypes.windll.user32.SetProcessDPIAware()

    def _crop(self):
        self.w -= (self.left + self.right)
        self.h -= (self.top + self.bottom)

    def _update(self):
        self._crop()
        self.monitor["top"] += self.top
        self.monitor["left"] += self.left
        self.monitor["width"] = self.w
        self.monitor["height"] = self.h

    def _scale(self):
        scale_w = self.monitor["width"]/self.w
        scale_h = self.monitor["height"]/self.h
        self.top = int(self.top*scale_w)
        self.left = int(self.left*scale_h)
        self.w = int(self.w*scale_w)
        self.h = int(self.h*scale_h)

    def _update_monitor(self):
        if self.monitor["width"] == self.w:
            self._update()
        else:
            self._scale()
            self._update()

    def test_screenshot(self):
        img = np.asarray(self.mss.grab(self.monitor))[:,:,:3]
        img =  cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
        cv2.imshow('screen location',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @background(max_prefetch=1)
    def screenshot(self):
        """Generate and preprocess screenshot"""

        while True:
            img = np.asarray(self.mss.grab(self.monitor))[:,:,:3]
            img =  cv2.resize(img, (224, 224)) / 255.0
            yield img


def connect(port, socket_type=zmq.REQ):
    context = zmq.Context()
    socket = context.socket(socket_type)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket


def check_monitor_region():
    answ = input('Is monitor region correct?:[y/n]').lower()
    if answ == 'y':
        return True
    elif answ == 'n':
        print('Check if OBS script settings are correct and try again')
        return False
    else:
        print('Invalid input try again')
        return check_monitor_region()


def run_classifier(monitor, socket, args):
    # Loading time
    from tensorflow import keras

    path = os.path.dirname(os.path.realpath(__file__))
    verboseprint = print if args.v else lambda *args, **kwargs: None
    model = keras.models.load_model(os.path.join(path, 'mobilenet1.3.h5'))
    for img in monitor.screenshot():
        pred = model.predict(np.asarray([img]))[0][0]
        socket.send_pyobj({'msg': 'predict', 'pred': pred})
        socket.recv_pyobj()
        verboseprint(pred)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", help="verbose output", action="store_true")
    parser.add_argument("--port", help="socket port", type=int, default=5557)
    args = parser.parse_args()
    socket = connect(args.port)
    socket.send_pyobj({'msg': 'screen'})
    mon_info = socket.recv_pyobj()
    with mss.mss() as sct:
        monitor = Monitor(sct, mon_info)
        monitor.test_screenshot()
        correct = check_monitor_region()
        if correct:
            run_classifier(monitor, socket, args)


if __name__=='__main__':
    main()
