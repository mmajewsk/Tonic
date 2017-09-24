import struct
import orb_slam2py
import json
import pickle
import numpy as np
from io import BytesIO
import cv2

class SlamManager:
	def __init__(self, vocab='Vocabulary/ORBvoc.txt',
				 cam_settings='Examples/Monocular/TUM-MINE.yaml'):
		self.vocab = vocab
		self.cam_settings = cam_settings
		self.slam = orb_slam2py.System(vocab, cam_settings, orb_slam2py.eSensor.MONOCULAR, True)

	def add_image(self, img, timestamp):
		try:
			self.slam.TrackMonocular(img, timestamp)
		except Exception as e:
			print e
			return str(e)
		else:
			return '{ok}'

	def get_trajectory(self):
		trajectory_str = self.slam.GetKeyFrameTrajectoryTUM()
		return trajectory_str


	def process(self, data):
		request_type = data[0]
		print('request type :[{}]'.format(request_type))
		if request_type == 'a':
			timestamp_serialized = data[1:9]
			timestamp = struct.unpack('d',timestamp_serialized)[0]
			img_serialized = data[9:]
			img_serialized = bytearray(img_serialized)
			img_serialized= np.array(img_serialized,dtype=np.uint8)
			img = cv2.imdecode(img_serialized,flags=cv2.IMREAD_UNCHANGED)
			result = self.add_image(img, timestamp)
		elif request_type == b't':
			traj = self.get_trajectory()
			if traj == '':
				return '{0}'
			else:
				return '{'+traj+'}'
		else:
			result = 'Error'
		response = result
		return response

	def close(self):
		self.slam.Shutdown()

	def __del__(self):
		self.close()