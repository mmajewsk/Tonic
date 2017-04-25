import numpy as np
import cv2
import socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import sys

import os
import argparse
import json
import time
import socket


class SetSteering(QThread):
	def __init__(self, app, intake_name=None, dump=True, turn_on=True):
		self.intake_name = intake_name
		self.dump = dump
		self.app = app
		QThread.__init__(self)
		self.socket = socket.socket()
		self.socket.connect(('192.168.1.212',2203))
		self.steering_log = []
		self.to_letters_dict = {87:'w', 83:'s', 68:'d', 65:'a'}
		if turn_on:
			self.steering = None#Steering()
			self.timer2 = QTimer()
			self.timer2.timeout.connect(self.ask_keys)
			self.timer2.start(28)

	def ask_keys(self):
		self.send(self.app.keys)

	def signal_to_string(self, signal):
		rval = " "
		for key in signal:
			if signal[key]:
				rval += self.to_letters_dict[key]
		return rval

	def send(self, keys):
		signal = self.signal_to_string(keys)
		self.socket.send(signal.encode())
		self.steering_log.append((str(keys), time.time()))

	def __del__(self):
		if self.steering is not None:
			self.socket.close()
		if self.dump is True:
			with open('../data_intake/{}/steering.json'.format(self.intake_name), 'w') as f:
				f.write(json.dumps(self.steering_log))


class GetCameraImage(QThread):
	image_downloaded = pyqtSignal(np.ndarray)

	def __init__(self):
		QThread.__init__(self)
		self.client_socket = None
		self.binary_stream = None
		self.client_socket = socket.socket()
		host = '192.168.1.212'  # - local
		# host = 'masterday.hopto.org'
		self.client_socket.connect((host, 2201))
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
				#print('emitting {}'.format(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
				self.image_downloaded.emit(frame)
			# print('emitted{}'.format(time.time()))
			# return image


class MainApp(QWidget):
	def __init__(self,
				intake_name=None,
				video=None,
				steering=None,
				dump_video=None,
				dump_steering=None
				):
		QWidget.__init__(self)
		self.intake_name = intake_name
		if intake_name is not None:
			self.intake_path = '../data_intake2/{}'.format(intake_name)
			if not os.path.exists(self.intake_path):
				os.makedirs(self.intake_path)
		self.video_size = QSize(320, 240)
		self.steering = steering
		self.video = video
		if self.steering:
			self.setup_steering(intake_name=self.intake_name, dump=dump_steering, turn_on=self.steering)
		if self.video:
			self.setup_camera(dump=dump_video, turn_on=self.video)
		self.setup_ui()

	def close(self):
		del self.set_steering

	def setup_steering(self, **kwargs):
		self.keys = {65: False, 83: False, 68: False, 87: False}  # asdw
		self.thread_steering = QThread()
		self.set_steering = SetSteering(self, **kwargs)
		self.set_steering.moveToThread(self.thread_steering)

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

	def setup_camera(self, turn_on=False, dump=False):
		"""Initialize camera.
		"""
		self.frame = np.zeros((10, 10, 3))
		self.thread_video = QThread()
		self.get_camera = GetCameraImage()
		self.get_camera.image_downloaded[np.ndarray].connect(self.add_image)
		self.get_camera.moveToThread(self.thread_video)
		self.timer = QTimer()
		self.frame_number = 0
		self.video = turn_on
		self.dump_video = dump
		self.timer.timeout.connect(self.handle_camera)
		self.timer.start(30)
		self.get_camera.start()

	def handle_camera(self):
		#if self.video:
		self.display_video_stream()
		#if self.dump_video:
		#	self.save_video_stream()

	def add_image(self, frame):
		self.frame = frame

	def save_video_stream(self):
		cv2.imwrite('../data_intake/{}/frame{:>05}_{}.jpg'.format(self.intake_name, self.frame_number, time.time()),
					self.frame)
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
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('-v', dest='video', action='store_true',
						help='video on')
	parser.add_argument('-s', dest='steering', action='store_true',
						help='steering on')
	parser.add_argument('--dump_video', dest='dump_video', action='store_false', help='if folder is given, dump video')
	parser.add_argument('--dump_steering', dest='dump_steering', action='store_false',
						help='if folder is given, dump video')
	parser.add_argument('folder', metavar='folder', type=str, nargs=argparse.REMAINDER, default=None,
						help='where to store data dump')

	args = parser.parse_args()
	app = QApplication(sys.argv)
	win = MainApp(intake_name=args.folder,
				  video=args.video,
				  steering=args.steering,
				  dump_video=args.dump_video,
				  dump_steering=args.dump_steering
				  )
	win.show()
	sys.exit(app.exec_())
