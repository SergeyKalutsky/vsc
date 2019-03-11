import zmq
import mss
import time
import random
import numpy as np
from prefetch_generator import BackgroundGenerator
from tensorflow import keras
from PIL import Image

img_size = (224, 224)
# model2 = keras.models.load_model('mobilenet1.2.h5')
# model1 = keras.models.load_model('mobilenet1.3.h5')

def preprocess_img(sct):
    global monitor
    #Generate and preprocess screenshot
    while True:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img = img.resize(img_size)
        img = np.asarray(img)[..., ::-1] / 255.0 
        yield monitor


def predict(img):
    # pred1 = model1.predict(np.array([img]))[0][0]
    # pred2 = model2.predict(np.array([img]))[0][0]
    # pred = np.mean([pred1, pred2])
    # return pred
    pass

def update_monitor(sct):
    sct.monitors[0]['width'] = random.randint(0, 1920)
    sct.monitors[0]['height'] = random.randint(0, 1080)

if __name__=='__main__':
    # context = zmq.Context()
    # socket = context.socket(zmq.REQ)
    # socket.connect("tcp://localhost:5557")
    with mss.mss() as sct:
        for img in BackgroundGenerator(preprocess_img(sct)):
            # pred = predict(img)
            print(img)
            update_monitor(sct)
            time.sleep(0.5)
            # socket.send (str(pred).encode('utf-8'))
            # socket.recv()
