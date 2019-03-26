import os
import zmq
import mss
import json
import argparse
import numpy as np
from monitor import Monitor


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


def run_classifier(monitor, socket):
    from tensorflow import keras

    verboseprint = print if args.v else lambda *args, **kwargs: None
    model = keras.models.load_model(os.path.join(ROOT_DIR, 'mobilenet1.3.h5'))
    for img in monitor.screenshot():
        pred = model.predict(np.asarray([img]))[0][0]
        socket.send_pyobj({'msg': 'predict', 'pred': pred})
        socket.recv_pyobj()
        verboseprint(pred)


def main():
    socket = connect(args.port)
    socket.send_pyobj({'msg': 'screen'})
    mon_info = socket.recv_pyobj()
    with mss.mss() as sct:
        monitor = Monitor(sct, mon_info)
        monitor.test_screenshot()
        correct = check_monitor_region()
        if correct:
            run_classifier(monitor, socket)


if __name__=='__main__':
    ROOT_DIR = path = os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", help="verbose output", action="store_true")
    parser.add_argument("--port", help="socket port", type=int, default=5557)
    args = parser.parse_args()
    main()
