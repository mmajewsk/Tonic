from slam_client import QtSlamClientManager
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

class MainApp(QThread):
	def __init__(self):
		QThread.__init__(self)
		self.qscm = QtSlamClientManager()
		self.th = QThread()
		self.qscm.connect()
		self.qscm.moveToThread(self.th)
		self.qscm.start()
		self.semaphore = True
		self.response_data = ' '
		self.qscm.response[bytes].connect(self.semaphore_off)

	def semaphore_off(self, response):
		self.semaphore = False
		self.response_data = response

	def run(self):
		data_path = r'C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3'
		df_path = r"C:\repositories\rgb.txt"
		dataframe = pd.read_csv(df_path, skiprows=[0, 1, 2], names=['timestamp', 'filename'], sep=' ')
		time.sleep(3)
		i = 0
		prev = None
		print('running')
		for i, (timestamp, filename) in dataframe.iterrows():
			impath = os.path.join(data_path, filename)
			img = cv2.imread(impath)
			assert img is not None, "Error while reading image {}".format(impath)
			#logger.debug("Sending with timestamp {}".format(timestamp))
			self.qscm.image_to_add.emit(img, timestamp)
			while self.semaphore:
				QApplication.processEvents()
				time.sleep(0.05)
			self.semaphore = True
			if prev is None:
				time.sleep(0.5)
				prev = timestamp
			else:
				time.sleep(timestamp-prev)
				prev = timestamp
			if i%50 == 0:
				self.qscm.trajectory.emit('')
				while self.semaphore:
					QApplication.processEvents()
					time.sleep(0.05)
				print("****TRAJ***************************")
				print(self.response_data)
				print("*************************************")
				self.response_data = ''
				self.semaphore = True




def using_q_thread():
	app = QCoreApplication([])
	thread = MainApp()
	th = QThread()
	thread.finished.connect(app.exit)
	thread.moveToThread(th)
	thread.start()
	sys.exit(app.exec_())


if __name__ == "__main__":
	using_q_thread()