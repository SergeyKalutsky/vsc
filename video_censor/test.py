import cv2
import mss
import numpy as np
import time

with mss.mss() as sct:
	count = 0
	while True:
	    img = np.asarray(sct.grab(sct.monitors[0]))[:,:,:3]
	    img = cv2.resize(img, (244, 244)) / 255.0
	    time.sleep(0.016)
	    cv2.imwrite(f'screens/{count}.png', img)
	    count += 1
