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

from clients import QTVideoClient, QTSteeringClient
from dataset import dump_dataframe

from logic import logic_layers


class Controller:
	def __init__(self,
				 video_client: QTVideoClient = None,
				 intake_name: str = None,
				 steering_client: QTSteeringClient = None,
				 dump_video: bool = False,
				 dump_steering: bool = False):
		self.main_dump_folder = '../../data_intake2'
		self.video_client = video_client
		self.intake_name = intake_name[0] if intake_name else None
		self.steering_client = steering_client
		self.dump_video = dump_video
		self.dump_steering = dump_steering
		self.view = None
		if self.intake_name:
			self.intake_path = os.path.join(self.main_dump_folder, self.intake_name)
			if not os.path.exists(self.intake_path):
				os.makedirs(self.intake_path)
		self.setup_logic_pipeline()

	def setup_logic_pipeline(self):
		self.pipeline = logic_layers

	def connect_steering(self, view):
		self.view = view
		self.thread_steering = QThread()
		self.steering_client.connect_controller(self)
		self.steering_client.moveToThread(self.thread_steering)

	@property
	def keys(self):
		#@TODO this must be fixed to handle the net commands
		if self.view:
			self._keys = self.view.keys
		else:
			return None
		return self._keys

	@property
	def frame(self):
		if self.dump_video:
			self.save_video_stream()
		return self._frame.copy()

	def connect_video(self):
		"""Initialize camera.
		"""
		self._frame = np.zeros((10, 10, 3))
		self.thread_video = QThread()
		self.video_client.image_downloaded[np.ndarray].connect(self.add_image)
		self.video_client.connect()
		self.video_client.moveToThread(self.thread_video)
		self._frame_number = 0
		self.video_client.start()

	def add_image(self, frame):
		self._clean_frame = frame.copy()
		frame, self._keys = self.apply_logic_pipeline(frame, self.keys)
		self._frame = frame

	def save_video_stream(self):
		picname = 'frame{:>05}_{}.jpg'.format(self._frame_number, time.time())
		picpath = os.path.join(self.intake_path, picname)
		if self._clean_frame.shape[0] > 20:
			frame = cv2.cvtColor(self._clean_frame, cv2.COLOR_RGB2BGR)
			cv2.imwrite(picpath, frame)
		self._frame_number += 1

	def apply_logic_pipeline(self, frame, keys):
		if frame.shape[0] > 20:
			for layer_name, layer in self.pipeline.items():
				frame, kwrgs = layer.action(frame=frame, keys=keys)
				keys = kwrgs['keys']
		return frame, keys

	def close(self):
		if self.steering_client and self.dump_steering:
			self.steering_client.dump_log(self.intake_path)
		if self.intake_name:
			dump_dataframe(self.intake_path)


	def __del__(self):
		self.close()


class MainApp(QWidget):
	def __init__(self, controller):
		QWidget.__init__(self)
		self.controller = controller
		self.intake_path = None
		if self.controller.steering_client:
			self.keys = self.controller.steering_client.key_events()
			self.setup_steering()
		else:
			self.keys = {}
		if self.controller.video_client:
			self.setup_camera()
		self.setup_logic_pipeline()
		self.setup_ui()

	def setup_logic_pipeline(self):
		self.pipeline = logic_layers

	def setup_steering(self):
		self.keys[17] = False
		self.controller.connect_steering(self)

	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		if self.controller.video_client:
			size = self.controller.video_client.video_size
		else:
			size = (320,240)
		video_size = QSize(*size)
		self.image_label.setFixedSize(video_size)

		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close)

		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.main_layout.addWidget(self.quit_button)

		self.setLayout(self.main_layout)

	def setup_camera(self):
		"""Initialize camera.
		"""
		self.timer = QTimer()
		self.timer.timeout.connect(self.refresh_view)
		self.timer.start(60)
		self.controller.connect_video()

	def refresh_view(self):
		if self.controller.video_client:
			frame = self.controller.frame
			self.display_video_stream(frame)

	def display_video_stream(self, frame):
		image = QImage(frame, frame.shape[1], frame.shape[0],
					   frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))

	def keyPressEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_Control]:
			self.keys[event.key()] = True

	def keyReleaseEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_Control]:
			self.keys[event.key()] = False

	def close(self):
		del self.controller
		QWidget.close(self)