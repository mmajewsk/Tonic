#http://picamera.readthedocs.io/en/release-1.10/recipes2.html#rapid-capture-and-streaming

import io
import socket
#import cv2
import pandas as pd
import os
import time
import numpy as np
from scipy import ndimage
from datetime import datetime

host ='127.0.0.1'
port = 2201
server = socket.socket()
server.bind((host, port))
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()
binary_stream = connection.makefile('rb')


folder = r'/mnt/c/Users/hawker/Dropbox/Public/selfie_car/data_intake3/v1.20'
images = os.listdir(folder)
images = filter(lambda x: ".jpg" in x, images)
images = sorted(images)
#images = map(lambda x: (x.split("_")[1][:-4], x), images)
images = map(lambda x: os.path.join(folder, x), images)

time.sleep(2)


for imgname in images:
	time.sleep(2)
	print(imgname)
	img = ndimage.imread(imgname)
	binary_stream.flush()
	binary_stream.write(img.tobytes())


binary_stream.close()
server.close()