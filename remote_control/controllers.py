import os
import time
import json

import cv2
import numpy as np

from clients import QTVideoClient, QTSteeringClient, QTImuClient, ClientSink
from dataset import dump_dataframe, join_imu
from logic import logic_layers, ImuKeeper, Imu, Mapper

def make_intake_path(intake_name):
	main_dump_folder = '../../data_intake4'
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
				 dump_steering: bool = False,
				 dump_odo: bool = False):
		BaseController.__init__(self, intake_name)
		self.client_sink=client_sink
		self.dump_video = dump_video
		self.dump_steering = dump_steering
		self.dump_odo = dump_odo
		self.view = None
		self.setup_logic_pipeline()
		self._frame_number = None
		self._timestamp = None
		self.odo_data = dict(left=[], right=[])

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

	def connect_odo(self):
		self.odo_data = dict(left=[],right=[])
		self.client_sink.start_odo()
		self.client_sink.connect_to_odo(self.add_odo)

	def add_image(self, frame):
		img = frame[0]
		self._timestamp = frame[1]
		self._clean_frame = img.copy()
		img, self._keys = self.apply_logic_pipeline(img, self.keys)
		self._frame = img

	def add_odo(self, odo_response):
		self.odo_data['left']+=odo_response['left']
		self.odo_data['right']+=odo_response['right']

	def save_video_stream(self):
		if self._timestamp is None:
			return
		picname = 'frame{:>05}_{}.jpg'.format(self._frame_number, self._timestamp)
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
		if self.client_sink.odo_client and self.dump_odo:
			with open(os.path.join(self.intake_path, 'odo_data.json'), 'w') as f:
				json.dump(self.odo_data,f)
		if self.intake_name:
			#dump_dataframe(self.intake_path)
			pass


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
		if self.client_sink.slam_client:
			self.connect_slam()
		self.mapper = Mapper()
		self.trajectory = b""

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

	def connect_slam(self):
		self.client_sink.start_slam()
		self.client_sink.connect_slam(self.set_trajectory)

	def set_trajectory(self, traj):
		self.trajectory = traj

	def get_slam_trajectory(self):
		self.client_sink.slam_client.trajectory_request.emit()

	def map(self):
		if self.client_sink.video_client:
			return self.mapper.update(self._frame, angle=self.data[0])
		return None

	def add_image(self, frame: np.ndarray):
		self._frame = frame[0].copy()
		timestamp = frame[1]
		if self.client_sink.slam_client is not None:
			self.client_sink.slam_client.image_to_send.emit(self._frame, timestamp)

	def add_data(self, raw_data: np.ndarray):
		#self.data = self.imu_processor.imu_from_raw(raw_data)
		try:
			self.data = self.imu_processor.rotation(raw_data).acc
		except ValueError as e:
			raise e

	def close(self):
		if self.dump_imu:
			self.imu_processor.dump_logs()
			with open(os.path.join(self.intake_path,'slam_trajectory.csv'),'w') as f:
				f.write(self.trajectory.decode())
			join_imu(self.intake_path)


