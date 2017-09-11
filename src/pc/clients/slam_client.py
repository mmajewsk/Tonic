from client import Client
import logging
import queue
import time
from PyQt5.Qt import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import cv2
import struct
import numpy as np

logging.basicConfig()
logger = logging.getLogger('SlamClient.ubu.src')
logger.setLevel(logging.DEBUG)

class SlamClient(Client):
	def __init__(
			self,
			server_adress=('127.0.0.1', 2207),
			connect=True,
	):
		super(SlamClient, self).__init__(server_adress, connect)

	def get_data(self):
		pass

	def run(self):
		broadcast = True
		while broadcast:
			try:
				if self._data is not None:
					self.return_data(self._data)
					self.get_data()
			except Exception as e:
				logging.error(e)
				broadcast = False
			else:
				continue

class QTSlamClient(SlamClient, QThread):
	data = pyqtSignal(bytes)

	def __init__(self, manager, *args, **kwargs):
		QThread.__init__(self)
		SlamClient.__init__(self, *args, **kwargs)
		self.manager = manager
		self.data[bytes].connect(self.add_data)
		self._data = None
		self._result = ' '

	def __enter__(self):
		self.connect()

	def __exit__(self, type, value, traceback):
		self.__del__()

	def add_data(self, data):
		self._data = data

	def request_result(self):
		self._result = None

	def get_data(self):
		result = self.client_socket.recv(1024)
		self.manager.response.emit(result)
		self._result = None

	def return_data(self, data):
		self.client_socket.send(data)
		self._data = None
		self._result = None


class QtSlamClientManager(QThread):
	response = pyqtSignal(bytes)
	image_to_add = pyqtSignal(np.ndarray, float)
	trajectory = pyqtSignal(str)

	def __init__(self, *args, **kwargs):
		QThread.__init__(self)
		self.slam_client = QTSlamClient(self, *args, connect=False, **kwargs)
		self.result = ''
		self._image_to_add = None
		self.image_queue = queue.Queue()
		self.response[bytes].connect(self.get_result)
		self.trajectory[str].connect(self.set_trajectory)
		self.image_to_add[np.ndarray, float].connect(self.add_image)
		self.thread_slam = QThread()
		self._traj = ' '
		self.slam_client.moveToThread(self.thread_slam)
		self.slam_client.start()

	def send_image(self, img, timestamp):
		img_bytes = cv2.imencode('.jpg', img)[1].tostring()
		#logger.info("Sending {}".format(timestamp))
		timestamp = bytes(struct.pack("d", timestamp))
		flag = bytes(struct.pack("c", b'a'))
		data = flag+timestamp+img_bytes
		self.slam_client.data.emit(data)

	def get_result(self, result):
		self.result = result

	def get_trajectory(self):
		self.slam_client.data.emit(b't\xff\xd8\xff\xd9')
		return self.result

	def add_image(self, img, timestamp):
		self.image_queue.put((img, timestamp))

	def set_trajectory(self, traj):
		self._traj = traj

	def connect(self):
		self.slam_client.connect()

	def run(self):
		while True:
			if not self.image_queue.empty():
				img, timestamp = self.image_queue.get()
				self.send_image(img, timestamp)
				QApplication.processEvents()
				# logger.debug("server response{}".format(qscm.result))
				while self.result == b' ':
					# logger.debug('Waiting for server response')
					time.sleep(0.05)
					QApplication.processEvents()
				# logger.debug("server response{}".format(qscm.result))
				if self.result != b' ':
					self.response.emit(b'ok')
					self.result = b' '
			if self._traj == '':
				logger.info('Getting trajectory')
				self.get_trajectory()
				while self.result == b' ':
					time.sleep(0.05)
					QApplication.processEvents()
					#logger.debug("server response{}".format(self.result))
				if self.result != b' ':
					self._traj = self.result.decode()
					self.trajectory.emit(self._traj)
					self.result = b' '