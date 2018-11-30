import multiprocessing
from async_slam_client import AsyncSlamClient, asyncore
import cv2
import time
import pandas as pd
import os
import logging
from PyQt5.Qt import QApplication, QThread
from PyQt5.QtCore import QCoreApplication
import sys

logging.basicConfig()
logger = logging.getLogger('slamclienttest.sandbox.pc.src')
logger.setLevel(logging.DEBUG)

import struct

def image_to_ata(img, timestamp):
	img_bytes = cv2.imencode('.jpg', img)[1].tostring()
	# logger.info("Sending {}".format(timestamp))
	timestamp = bytes(struct.pack("d", timestamp))
	flag = bytes(struct.pack("c", b'a'))
	data = flag + timestamp + img_bytes
	return data

if __name__ == "__main__":
	data_path = r'C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3'
	df_path = r"C:\repositories\rgb.txt"
	dataframe = pd.read_csv(df_path, skiprows=[0, 1, 2], names=['timestamp', 'filename'], sep=' ')
	time.sleep(3)
	i = 0
	prev = None
	print('running')
	manager = multiprocessing.Manager()
	task = manager.Queue()
	result = manager.Queue()
	client = AsyncSlamClient(('127.0.0.1', 2207),task,result)
	for i, (timestamp, filename) in dataframe.iterrows():
		impath = os.path.join(data_path, filename)
		img = cv2.imread(impath)
		assert img is not None, "Error while reading image {}".format(impath)
		#logger.debug("Sending with timestamp {}".format(timestamp))
		img_data = image_to_ata(img, timestamp)
		task.put(img_data)
		while result.empty():
			try:
				asyncore.loop()
			except asyncore.ExitNow:
				pass
		print('response get')
		print(result.get())






