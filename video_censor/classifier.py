import zmq
import mss
import cv2
import numpy as np
from tensorflow import keras
from prefetch_generator import BackgroundGenerator

img_size = (224, 224)
model = keras.models.load_model('mobilenet1.3.h5')


def preprocess_img():
    #Generate and preprocess screenshot
    while True:
        img = np.asarray(sct.grab(sct.monitors[1]))[:,:,:3]
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
    with mss.mss() as sct:
        for img in BackgroundGenerator(preprocess_img()):
            pred = predict(img)
            print(pred)
            socket.send_json({"action": "update screen",
                              "prediction": float(pred)})
            socket.recv()
