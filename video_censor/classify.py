import zmq
import mss
import ast
import numpy as np
from prefetch_generator import BackgroundGenerator
from tensorflow import keras
from PIL import Image

img_size = (224, 224)
model = keras.models.load_model('mobilenet1.3.h5')


def preprocess_img(sct):
    #Generate and preprocess screenshot
    while True:
        sct_img = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img = img.resize(img_size)
        img = np.asarray(img)[..., ::-1] / 255.0 
        yield img


def predict(img):
    pred = model.predict(np.array([img]))[0][0]
    return pred


def update_monitor(sct, coor):
    if sct.monitors[1] != coor:
        sct.monitors[1] = coor


def connect():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5557")
    return socket


if __name__=='__main__':
    socket = connect()
    with mss.mss() as sct:
        for img in BackgroundGenerator(preprocess_img(sct)):
            pred = predict(img)
            print(pred)
            socket.send(str(pred).encode('utf-8'))
            coor = ast.literal_eval(socket.recv().decode('utf-8'))
            update_monitor(sct, coor)

