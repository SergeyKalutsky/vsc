import os
import zmq
import mss
import json
import cv2
import numpy as np
import random
# from tensorflow import keras
from prefetch_generator import background


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


def update_monitor(monitor, screen_part):
    monitor["top"] += screen_part["top"]
    monitor["left"] += screen_part["left"]
    monitor["width"] = screen_part["width"]
    monitor["height"] = screen_part["height"]
    return monitor


def connect(port):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket

def parse_conf():
    with open("conf.json", 'r') as f:
        conf = json.load(f)
    return conf["monitor"], conf["coordinates"], conf["port"]


if __name__=='__main__':
    mon, cor, port = parse_conf()
    producer = connect(port)
    # model = keras.models.load_model('mobilenet1.3.h5')
    with mss.mss() as sct:
        monitor = update_monitor(sct.monitors[mon], cor)
        for img in screenshot(monitor):
            pred = random.random()
            print(pred)
            producer.send_pyobj(pred)

