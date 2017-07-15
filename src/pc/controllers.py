import os
import time

import cv2
import numpy as np

from clients import QTVideoClient, QTSteeringClient, QTImuClient, ClientSink
from dataset import dump_dataframe
from logic import logic_layers, ImuKeeper, Imu, Mapper

def make_intake_path(intake_name):
	main_dump_folder = '../../data_intake3'
	intake_path = os.path.join(main_dump_folder, intake_name)
	if not os.path.exists(intake_path):
		os.makedirs(intake_path)
	return intake_path

class BaseController:
	def __init__(self, intake_name: str = None):
		intake_name = intake_name[0] if intake_name else None
		self.intake_name = intake_name
		if self.intake_name:
			self.intake_path = make_intake_path(intake_name)
		else:
			self.intake_path = None


class Controller(BaseController):
	def __init__(self,
				 client_sink:ClientSink = None,
				 intake_name: str = None,
				 dump_video: bool = False,
				 dump_steering: bool = False):
		BaseController.__init__(self, intake_name)
		self.client_sink=client_sink
		self.dump_video = dump_video
		self.dump_steering = dump_steering
		self.view = None
		self.setup_logic_pipeline()

	def setup_logic_pipeline(self):
		self.pipeline = logic_layers

	def connect_steering(self, view):
		self.view = view
		self.client_sink.start_steering(self)


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
		self._frame_number = 0
		self._clean_frame = None
		self.client_sink.start_video()
		self.client_sink.connect_to_video(self.add_image)

	def add_image(self, frame):
		self._clean_frame = frame.copy()
		frame, self._keys = self.apply_logic_pipeline(frame, self.keys)
		self._frame = frame

	def save_video_stream(self):
		picname = 'frame{:>05}_{}.jpg'.format(self._frame_number, time.time())
		picpath = os.path.join(self.intake_path, picname)
		if isinstance(self._clean_frame, np.ndarray) and self._clean_frame.shape[0] > 20:
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
		if self.client_sink.steering_client and self.dump_steering:
			self.client_sink.steering_client.dump_log(self.intake_path)
		if self.intake_name:
			dump_dataframe(self.intake_path)

	def __del__(self):
		self.close()

class MapController(BaseController):
	def __init__(self, client_sink:ClientSink=None, intake_name : str=None, dump_imu : bool = False):
		BaseController.__init__(self, intake_name)
		self.dump_imu = dump_imu
		self.map_frame_size = (800, 800)
		self.client_sink = client_sink
		self.imu_processor = ImuKeeper(dump_imu=dump_imu, dump_dir=self.intake_path)
		if self.client_sink.imu_client:
			self.connect_imu()
		if self.client_sink.video_client:
			self.connect_video()
		self.mapper = Mapper()

	def connect_imu(self):
		self.data = [0,0,0]
		self.client_sink.start_imu()
		self.client_sink.connect_to_imu(self.add_data)

	def connect_video(self):
		"""Initialize camera.
		"""
		self._frame = np.zeros((10, 10, 3))
		self._frame_number = 0
		self._clean_frame = None
		#self.client_sink.start_video()
		self.client_sink.connect_to_video(self.add_image)

	def map(self):
		if self.client_sink.video_client:
			return self.mapper.update(self._frame, angle=self.data[0])
		return None

	def add_image(self, frame: np.ndarray):
		self._frame = frame.copy()

	def add_data(self, raw_data: np.ndarray):
		#self.data = self.imu_processor.imu_from_raw(raw_data)
		self.data = self.imu_processor.rotation(raw_data).acc

	def close(self):
		if self.dump_imu:
			self.imu_processor.dump_logs()