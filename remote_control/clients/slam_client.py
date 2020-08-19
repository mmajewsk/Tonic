import queue
from clients.client import Client
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


class QtSlamClient(Client, QThread):
	image_response = pyqtSignal(bytes)
	image_to_send = pyqtSignal(np.ndarray, float)
	trajectory_response = pyqtSignal(bytes)
	trajectory_request = pyqtSignal()

	def __init__(self, *args, **kwargs):
		Client.__init__(self, *args, **kwargs)
		QThread.__init__(self)
		self.send_queue = queue.Queue()
		self.result_queue = queue.Queue()
		self.payload = b''
		self.image_to_send[np.ndarray, float].connect(self.send_image)
		self.trajectory_request.connect(self.request_trajectory)


	def send_image(self, img, timestamp):
		img_bytes = cv2.imencode('.jpg', img)[1].tostring()
		#logger.info("Sending {}".format(timestamp))
		timestamp = bytes(struct.pack("d", timestamp))
		flag = bytes(struct.pack("c", b'a'))
		data = flag+timestamp+img_bytes
		self.send_queue.put(data)

	def request_trajectory(self):
		self.send_queue.put(b't\xff\xd8\xff\xd9')

	def handle_write(self):
		data = self.send_queue.get()
		self.client_socket.send(data)
		time.sleep(0.07)

	def emit_response(self, data):
		if data == b'ok':
			self.image_response.emit(b'ok')
		else:
			self.trajectory_response.emit(data)

	def handle_read(self):
		self.payload += self.client_socket.recv(1024)
		first = self.payload.find(b'{')
		last = self.payload.find(b'}')
		if first != -1 and last != -1:
			data = self.payload[first+1:last]
			self.payload = self.payload[last+1:]
			self.result_queue.get()
			self.emit_response(data)
			time.sleep(0.07)

	def return_data(self, frame):
		pass

	def run(self):
		broadcast = True
		while broadcast:
			try:
				if not self.send_queue.empty():
					self.handle_write()
					self.result_queue.put('awaiting')
				if not self.result_queue.empty():
					self.handle_read()
			except Exception as e:
				logging.error(e)
				broadcast = False
			else:
				continue