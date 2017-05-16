from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import cv2
import socket
from abc import ABCMeta, abstractmethod
import multiprocessing
import time

class VideoClient:
	__metaclass__ =ABCMeta

	def __init__(self, server_adress=('192.168.1.212',2201), connect=False):
		self.client_socket = None
		self.binary_stream = None
		self.client_socket = None
		self.server_adress = server_adress
		if connect:
			self.connect()
		# host = 'masterday.hopto.org'

	def connect(self):
		self.client_socket = socket.socket()
		self.client_socket.connect(self.server_adress)
		self.binary_stream = self.client_socket.makefile('rb')
		self.payload = b' '

	def preprocess_image(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.flip(img, 1)
		img = cv2.flip(img, 0)
		return img

	@abstractmethod
	def return_data(self, frame):
		pass

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
				frame = self.preprocess_image(image)
				#print('emitting {}'.format(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
				self.return_data(frame)
			# print('emitted{}'.format(time.time()))

	def __del__(self):
		if self.binary_stream is not None:
			self.binary_stream.close()
		if self.client_socket is not None:
			self.client_socket.close()

class QTVideoClient(VideoClient, QThread):
	image_downloaded = pyqtSignal(np.ndarray)
	def __init__(self, *args, **kwargs):
		QThread.__init__(self)
		VideoClient.__init__(self, *args, **kwargs)

	def __enter__(self):
		self.connect()

	def __exit__(self, type, value, traceback):
		self.__del__()

	def return_data(self, frame):
		self.image_downloaded.emit(frame)


class MultiVideoClient(VideoClient, multiprocessing.Process):
	def __init__(self, task_queue, result_queue, dt=0.1, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		VideoClient.__init__(self, *args, **kwargs)
		self.task_queue = task_queue
		self.result_queue = result_queue
		self.dt = dt

	def run(self):
		self.connect()
		VideoClient.run(self)

	def return_data(self, frame):
		_ = self.task_queue.get()
		self.task_queue.task_done()
		self.result_queue.put(frame)
		time.sleep(self.dt)