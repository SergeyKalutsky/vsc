import os
import zmq
import mss
import json
import argparse
import numpy as np
from .monitor import Monitor


ROOT_DIR = path = os.path.dirname(os.path.realpath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument("-v", help="verbose output", action="store_true")
parser.add_argument("--scrshot", help="make screenshot of a selected region", action="store_true")


def parse_conf():
    with open(os.path.join(ROOT_DIR, 'conf.json'), 'r') as f:
        conf = json.load(f)
    return conf["monitor"], conf["monitor_info"], conf["port"]


def connect(port, socket_type=zmq.REQ):
    context = zmq.Context()
    socket = context.socket(socket_type)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket


def main():
    args = parser.parse_args()
    mon, mon_info, port = parse_conf()
    verboseprint = print if args.v else lambda *args, **kwargs: None
    socket = connect(port)
    with mss.mss() as sct:
        monitor = Monitor(sct, mon, mon_info)
        if args.scrshot:
            monitor.test_screenshot()
        else:
            from tensorflow import keras
            model = keras.models.load_model(os.path.join(ROOT_DIR, 'mobilenet1.3.h5'))
            for img in monitor.screenshot():
                pred = model.predict(np.asarray([img]))[0][0]
                socket.send_pyobj(pred)
                socket.recv()
                verboseprint(pred)

if __name__=='__main__':
    main()
