import zmq
import mss
import cv2
import numpy as np
from tensorflow import keras
from prefetch_generator import background


model = keras.models.load_model('mobilenet1.3.h5')

@background(max_prefetch=1)
def preprocess_img(screen_part):
    #Generate and preprocess screenshot
    while True:
        img = np.asarray(sct.grab(screen_part))[:,:,:3]
        img =  cv2.resize(img, (224, 224)) / 255.0 
        yield img


def predict(img):
    pred = model.predict(np.asarray([img]))[0][0]
    return pred


def update_monitor(sct, coor):
    if sct.monitors[1] != coor:
        sct.monitors[1] = coor


def connect(port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")
    return socket


if __name__=='__main__':
    port = 5557
    socket = connect(port)
    socket.send_json({"action": "get screen region"})
    screen_part = socket.recv_json()
    with mss.mss() as sct:
        for img in preprocess_img(screen_part):
            pred = predict(img)
            print(pred)
            socket.send_json({"action": "update screen",
                              "prediction": float(pred)})
            socket.recv()
