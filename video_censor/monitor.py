import sys
import cv2
import ctypes
import platform
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
