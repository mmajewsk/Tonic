import argparse
import json
import os
import socket
import sys
import time

import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from clients.video_client import QTVideoClient
from clients.steering_client import SetSteering
from dataset import dump_dataframe

from logic import vision_layers
from logic import logic_layers

class MainApp(QWidget):
	def __init__(self,
				intake_name=None,
				video=None,
				steering=None,
				dump_video=None,
				dump_steering=None
				):
		QWidget.__init__(self)
		self.main_dump_folder = '../../data_intake2'
		self.intake_name = intake_name[0] if intake_name else None
		self.intake_path = None
		self.steering_server_adress = ('192.168.1.212',2203)
		if self.intake_name:
			self.intake_path = os.path.join(self.main_dump_folder, self.intake_name)
			if not os.path.exists(self.intake_path):
				os.makedirs(self.intake_path)
		self.video_size = QSize(320, 240)
		self.steering = steering
		self.video = video
		if self.steering:
			self.setup_steering(server_adress=self.steering_server_adress, intake_path=self.intake_path, dump=dump_steering, turn_on=self.steering)
		if self.video:
			self.setup_camera(dump=dump_video, turn_on=self.video)
		pipeline_dict = {'stop_sign': True, }
		self.setup_logic_pipeline(pipeline_dict)
		self.setup_ui()

	def close(self):
		self.set_steering.dump_log()
		if self.intake_name:
			dump_dataframe(self.intake_path)
		self.exit()

	def setup_logic_pipeline(self, pipeline_dict):
		self.pipeline = logic_layers





	def setup_steering(self, **kwargs):
		self.keys = SetSteering.key_events()
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
		self.get_camera = QTVideoClient()
		self.get_camera.image_downloaded[np.ndarray].connect(self.add_image)
		self.get_camera.connect()
		self.get_camera.moveToThread(self.thread_video)
		self.timer = QTimer()
		self.frame_number = 0
		self.video = turn_on
		self.dump_video = dump
		self.timer.timeout.connect(self.handle_camera)
		self.timer.start(60)
		self.get_camera.start()

	def handle_camera(self):
		if self.video:
			self.display_video_stream()
		if self.dump_video:
			self.save_video_stream()

	def add_image(self, frame):
		self.frame = frame

	def save_video_stream(self):
		picname = 'frame{:>05}_{}.jpg'.format(self.frame_number, time.time())
		picpath = os.path.join(self.intake_path, picname)
		if self.frame.shape[0]>20:
			frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
			cv2.imwrite(picpath, frame)
		self.frame_number += 1

	def apply_logic_pipeline(self, frame, keys):
		for layer in self.logic_pipeline:
			frame, keys = layer.action(frame, keys)
		return frame, keys

	def display_video_stream(self):
		frame = self.frame
		frame, self.keys = self.apply_logic_pipeline(frame, self.keys)
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
	parser.add_argument('--dump_video', dest='dump_video', action='store_true', help='if folder is given, dump video')
	parser.add_argument('--dump_steering', dest='dump_steering', action='store_true',
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
