import numpy as np
from PyQt5.QtCore import QThread
from clients.video_client import QTVideoClient
from clients.steering_client import QTSteeringClient
from clients.imu_client import ImuClient
from clients.slam_client import QtSlamClient

class ClientSink:
	def __init__(self, video_client: QTVideoClient = None,
				 steering_client:QTSteeringClient=None,
				 imu_client:ImuClient=None,
				 slam_client:QtSlamClient=None):
		self.video_client = video_client
		self.steering_client = steering_client
		self.imu_client = imu_client
		self.slam_client = slam_client

	def start_video(self):
		self.thread_video = QThread()
		self.video_client.connect()
		self.video_client.moveToThread(self.thread_video)
		self.video_client.start()

	def connect_to_video(self, method):
		self.video_client.data_downloaded[np.ndarray].connect(method)

	def start_steering(self, controller):
		self.thread_steering = QThread()
		self.steering_client.connect_controller(controller)
		self.steering_client.moveToThread(self.thread_steering)

	def start_imu(self):
		self.thread_imu = QThread()
		self.imu_client.connect()
		self.imu_client.moveToThread(self.thread_imu)
		self.imu_client.start()

	def connect_to_imu(self, method):
		self.imu_client.data_downloaded[np.ndarray].connect(method)

	def start_slam(self):
		self.thread_slam = QThread()
		self.slam_client.connect()
		self.slam_client.moveToThread(self.thread_slam)
		self.slam_client.start()

	def connect_slam(self, trajectory_receive_method):
		self.slam_client.trajectory_response[bytes].connect(trajectory_receive_method)