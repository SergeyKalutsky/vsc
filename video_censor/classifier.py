import sys
import os
import json
import argparse
import ctypes
import platform

import zmq
import mss
import cv2
import numpy as np
from tensorflow import keras
from prefetch_generator import background


parser = argparse.ArgumentParser()
parser.add_argument("-v", help="verbose output", action="store_true")

class Monitor():
    def __init__(self, monitor_num, monitor_info):
        self.monitor = sct.monitors[monitor_num]
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

    def tets_screenshot(self):
        sct_img = sct.grab(self.monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output="test.png")

    @background(max_prefetch=1)
    def screenshot(self):
        """Generate and preprocess screenshot"""

        while True:
            img = np.asarray(sct.grab(self.monitor))[:,:,:3]
            img =  cv2.resize(img, (224, 224)) / 255.0
            yield img


def connect(port, socket_type=zmq.REQ):
    context = zmq.Context()
    socket = context.socket(socket_type)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket


def parse_conf():
    with open("conf.json", 'r') as f:
        conf = json.load(f)
    return conf["monitor"], conf["monitor_info"], conf["port"]


if __name__=='__main__':
    args = parser.parse_args()
    mon, mon_info, port = parse_conf()
    model = keras.models.load_model('mobilenet1.3.h5')
    verboseprint = print if args.v else lambda *args, **kwargs: None
    socket = connect(port)
    with mss.mss() as sct:
        monitor = Monitor(mon, mon_info)
        for img in monitor.screenshot():
            pred = model.predict(np.asarray([img]))[0][0]
            socket.send_pyobj(pred)
            socket.recv()
            verboseprint(pred)
