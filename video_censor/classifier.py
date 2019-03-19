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

def mss_bugfix():
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

@background(max_prefetch=1)
def screenshot(monitor):
    """Generate and preprocess screenshot"""
    while True:
        img = np.asarray(sct.grab(monitor))[:,:,:3]
        img =  cv2.resize(img, (224, 224)) / 255.0
        yield img


def predict(img):
    pred = model.predict(np.asarray([img]))[0][0]
    return pred


def crop(size, crop):
    w, h = size
    top, left, right, bottom = crop
    w -= (left + right)
    h -= (top + bottom)
    return w, h

def scale(info):
    w, h =  info["source_size"]
    top, left, right, bottom = info["crop"]
    scale_x, scale_y = info["scale"]
    for val in [w, left, right]:
        val *= scale_x
    for val in [h, top, bottom]:
        val *= scale_y
    return w, h, top, left, right, bottom

def update_monitor(monitor, info):
    if monitor["width"] == info["source_size"][0]:
        w, h = crop(info["source_size"], info["crop"])
        monitor["top"] += info["crop"][0]
        monitor["left"] += info["crop"][1]
        monitor["width"] = w
        monitor["height"] = h
        scale = 0
    else:
        scale = monitor["width"]/info["source_size"][0]
        w, h = crop(info["source_size"], info["crop"])
        monitor["top"] += int(info["crop"][0]*scale)
        monitor["left"] += int(info["crop"][1]*scale)
        monitor["width"] = int(w*scale)
        monitor["height"] = int(h*scale)
    return monitor

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
    mss_bugfix()
    args = parser.parse_args()
    mon, mon_info, port = parse_conf()
    producer = connect(port)
    model = keras.models.load_model('mobilenet1.3.h5')
    verboseprint = print if args.v else lambda *args, **kwargs: None
    with mss.mss() as sct:
        monitor = update_monitor(sct.monitors[mon], mon_info)
        for img in screenshot(monitor):
            pred = predict(img)
            producer.send_pyobj(pred)
            producer.recv()
            verboseprint(pred)
