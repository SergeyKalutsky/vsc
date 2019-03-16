import os
import zmq
import mss
import json
import cv2
import numpy as np
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
	socket = context.socket(zmq.REQ)
	socket.connect(f"tcp://localhost:{port}")
	return socket

def parse_conf():
	cwd = os.getcwd()
	with open(os.path.join(cwd, "conf.json"), 'r') as f:
		conf = json.load(f)
	return conf["monitor"], conf["coordinates"] conf["port"]

if __name__=='__main__':
	mon, cor, port = parse_conf()
	socket = connect(port)
	model = keras.models.load_model('mobilenet1.3.h5')
	with mss.mss() as sct:
		monitor = update_monitor(mon, cor)
		for img in screenshot(monitor):
			exhange({"act": "stream censor",
				     "pred": float(predict(img))})

