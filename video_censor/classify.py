import mss
import time
import numpy as np
from prefetch_generator import BackgroundGenerator
from tensorflow import keras
from PIL import Image

img_size = (224, 224)
model = keras.models.load_model('mobilenet1.3.h5')
model1 = keras.models.load_model('mobilenet1.2.h5')


def preprocess_img():
    while True:
        sct_img = sct.grab(sct.monitors[0]) 
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img = img.resize((224, 224))
        img = np.asarray(img)[..., ::-1] / 255.0 
        yield img

def predict(img):
    pred = model.predict(np.array([img]))[0][0]
    pred1 = model1.predict(np.array([img]))[0][0]
    f_pred = np.mean([pred, pred1])
    print(f_pred)
    with open(r'communicator.txt', 'w') as f:
        f.write(str(round(f_pred, 3)))


if __name__=='__main__':
    with mss.mss() as sct:
        for img in BackgroundGenerator(preprocess_img()):
            predict(img)
