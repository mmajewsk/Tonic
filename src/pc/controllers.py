import os
import time

import cv2
import numpy as np
from PyQt5.QtCore import QThread

from clients import QTVideoClient, QTSteeringClient, QTImuClient
from dataset import dump_dataframe
from logic import logic_layers, ImuKeeper, Imu

def make_intake_path(intake_name):
	main_dump_folder = '../../data_intake3'
	intake_path = os.path.join(main_dump_folder, intake_name)
	if not os.path.exists(intake_path):
		os.makedirs(intake_path)
	return intake_path

class BaseController:
	def __init__(self, intake_name: str = None):
		self.intake_name = intake_name
		if self.intake_name:
			self.intake_path = make_intake_path(intake_name)

class Controller(BaseController):
	def __init__(self,
				 video_client: QTVideoClient = None,
				 intake_name: str = None,
				 steering_client: QTSteeringClient = None,
				 dump_video: bool = False,
				 dump_steering: bool = False):
		BaseController.__init__(self, intake_name)
		self.video_client = video_client
		self.intake_name = intake_name[0] if intake_name else None
		self.steering_client = steering_client
		self.dump_video = dump_video
		self.dump_steering = dump_steering
		self.view = None
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
		self.video_client.data_downloaded[np.ndarray].connect(self.add_image)
		self.video_client.connect()
		self.video_client.moveToThread(self.thread_video)
		self._frame_number = 0
		self.video_client.start()

	def add_image(self, frame):
		if self.frame.shape[0]>10:
			print("Image{}".format(np.sum(frame-self.frame)))
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

class MapController(BaseController):
	def __init__(self, imu_client:QTImuClient=None, intake_name : str=None, dump_imu : bool = False):
		BaseController.__init__(self, intake_name)
		self.dump_imu = dump_imu
		self.map_frame_size = (800, 800)
		self.imu_client = imu_client
		self.imu_processor = ImuKeeper()
		if self.imu_client:
			self.connect_imu()

	def connect_imu(self):
		self.data = Imu(np.zeros((1,9)))
		self.thread_imu = QThread()
		self.imu_client.data_downloaded[np.ndarray].connect(self.add_data)
		self.imu_client.connect()
		self.imu_client.moveToThread(self.thread_imu)
		self._frame_number = 0
		self.imu_client.start()

	def add_data(self, raw_data: np.ndarray):
		self.data = self.imu_processor.imu_from_raw(raw_data)

	def close(self):
		if self.dump_imu:
			self.imu_processor.dump_logs()