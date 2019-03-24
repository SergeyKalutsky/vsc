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
parser.add_argument("--port", help="socket port", type=int, default=5557)


def connect(port, socket_type=zmq.REQ):
    context = zmq.Context()
    socket = context.socket(socket_type)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket


def main():
    args = parser.parse_args()
    verboseprint = print if args.v else lambda *args, **kwargs: None
    socket = connect(args.port)
    socket.send_pyobj({'msg': 'screen'})
    mon_info = socket.recv_pyobj()
    with mss.mss() as sct:
        monitor = Monitor(sct, mon_info)
        if args.scrshot:
            monitor.test_screenshot()
        else:
            from tensorflow import keras
            
            model = keras.models.load_model(os.path.join(ROOT_DIR, 'mobilenet1.3.h5'))
            for img in monitor.screenshot():
                pred = model.predict(np.asarray([img]))[0][0]
                socket.send_pyobj({'msg': 'predict', 'pred': pred})
                socket.recv_pyobj()
                verboseprint(pred)

if __name__=='__main__':
    main()
