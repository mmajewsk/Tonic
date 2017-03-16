import numpy as np
import cv2
import socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import sys

import os

import json
import time
from usb_com import Steering

class SetSteering(QThread):

	def __init__(self, app, intake_name=None, create_timer=True, save_steering=True):
		self.intake_name = intake_name
		self.save_steering = save_steering
		self.app = app
		QThread.__init__(self)
		self.steering = None
		self.steering_log=[]
		if create_timer:
			self.steering = Steering()
			self.timer2 = QTimer()
			self.timer2.timeout.connect(self.ask_keys)
			self.timer2.start(28)

	def ask_keys(self):
		self.send(self.app.keys)

	def send(self, keys):
		self.steering.write_keys(keys)
		self.steering_log.append((str(keys),time.time()))

	def __del__(self):
		if self.steering is not None:
			self.steering.close() 
		if self.save_steering is True:
			with open('../data_intake/{}/steering.json'.format(self.intake_name),'w') as f:
				f.write(json.dumps(self.steering_log))

class GetCameraImage(QThread):
	image_downloaded = pyqtSignal(np.ndarray)

	def __init__ (self):
		QThread.__init__(self)
		self.client_socket = None
		self.binary_stream = None
		self.client_socket = socket.socket()
		host = '192.168.1.212' # - local
		#host = 'masterday.hopto.org'
		self.client_socket.connect((host,2201))
		self.binary_stream = self.client_socket.makefile('rb')
		self.payload = b' '

	def __del__(self):
		if self.binary_stream is not None:
			self.binary_stream.close()
		if self.client_socket is not None:
			self.client_socket.close()

	def run(self):
		broadcast = True
		frame = 1
		image_start = b'\xff\xd8'
		image_end = b'\xff\xd9'
		while broadcast:
			self.payload += self.binary_stream.read(1024)
			first = self.payload.find(image_start)
			last = self.payload.find(image_end)
			if first != -1 and last != -1:
				self.jpg = self.payload[first:last + 2]
				self.payload = self.payload[last + 2:]
				image = cv2.imdecode(np.fromstring(self.jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
				frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
				frame = cv2.flip(frame, 1)
				frame = cv2.flip(frame, 0)
				#print('emitting{}'.format(time.time()))
				self.image_downloaded.emit(frame)
				#print('emitted{}'.format(time.time()))
				#return image
		


class MainApp(QWidget):

	def __init__(self, intake_name=None):
		QWidget.__init__(self)
		self.intake_name = intake_name
		if intake_name is not None:
			self.intake_path = '../data_intake/{}'.format(intake_name)
			if not os.path.exists(self.intake_path):
				os.makedirs(self.intake_path)
		self.video_size = QSize(320, 240)
		self.setup_steering(intake_name=self.intake_name, save_steering=False, create_timer=True)
		self.setup_ui()
		self.setup_camera(just_save=False)

	def close(self):
		del self.set_steering

	def setup_steering(self, **kwargs):
		self.keys = {65: False, 83: False, 68: False, 87: False}#asdw
		self.thread = QThread()
		self.set_steering = SetSteering(self, **kwargs)
		self.set_steering.moveToThread(self.thread)
		

	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		self.image_label.setFixedSize(self.video_size)

		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close)

		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.main_layout.addWidget(self.quit_button)

		self.setLayout(self.main_layout)

	def setup_camera(self, just_save=True):
		"""Initialize camera.
		"""
		self.frame = np.zeros((10,10,3))
		self.thread = QThread()
		self.get_camera = GetCameraImage()
		self.get_camera.image_downloaded[np.ndarray].connect(self.add_image)
		self.get_camera.moveToThread(self.thread)
		self.timer = QTimer()
		self.frame_number=0
		fun = self.display_video_stream if not just_save else self.save_video_stream
		self.timer.timeout.connect(fun)
		self.timer.start(30)
		self.get_camera.start()

	def add_image(self, frame):
		self.frame = frame

	def save_video_stream(self):
		cv2.imwrite('../data_intake/{}/frame{:>05}_{}.jpg'.format(self.intake_name, self.frame_number, time.time()), self.frame)
		self.frame_number += 1

	def display_video_stream(self):
		frame = self.frame
		image = QImage(frame, frame.shape[1], frame.shape[0], 
					   frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))

	def keyPressEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
			self.keys[event.key()] = True
		

	def keyReleaseEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
			self.keys[event.key()] = False



if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainApp(sys.argv[1])
	win.show()
	sys.exit(app.exec_())



