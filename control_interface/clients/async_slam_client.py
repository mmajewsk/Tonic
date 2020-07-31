import struct
import cv2
import numpy as np
import socket
import asyncore
from PyQt5.Qt import QApplication
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal
# simple demo of the asyncore asyncore.dispatcher class.

class AsyncSlamClient(asyncore.dispatcher):
	def __init__ (self,server_adress, task_queue, result_queue):
		asyncore.dispatcher.__init__ (self)
		self.task_queue = task_queue
		self.result_queue = result_queue
		self.data_to_write = []
		self.payload = b''
		self.create_socket()#socket.AF_INET, socket.SOCK_STREAM)
		self.connect(server_adress)

	# once connected, send the account name
	def handle_connect(self):
		self.log('connected')

	# collect some more finger server output.
	def handle_read(self):
		#self.log('reading...')
		self.payload += self.recv(1024)
		#self.log(self.payload)
		first = self.payload.find(b'{')
		last = self.payload.find(b'}')
		if first != -1 and last != -1:
			data = self.payload[first+1:last]
			self.payload = self.payload[last+1:]
			self.result_queue.put(data)
			raise asyncore.ExitNow()

	def writable(self):
		return bool(self.data_to_write) or not self.task_queue.empty()

	def handle_write(self):
		#self.log('writing...')
		#self.log(len(self.data_to_write))
		if not self.task_queue.empty():
			self.data_to_write.append(self.task_queue.get())
		data = self.data_to_write[0]
		sent = self.send(data)
		#self.log("sent {} len(data) {}".format(sent, len(data)))
		if sent < len(data):
			remaining = data[sent:]
			self.data_to_write[0] = remaining
		else:
			del self.data_to_write[0]

	# the other side closed, we're done.
	def handle_close(self):
		self.close()

class QtAsyncSlamClient(QThread):
	image_response = pyqtSignal(bytes)
	image_to_send = pyqtSignal(np.ndarray, float)
	trajectory_response = pyqtSignal(bytes)
	trajectory_request = pyqtSignal()

	def __init__(self, server_adress):
		QThread.__init__(self)
		self.send_queue = Queue()
		self.receive_queue = Queue()
		self.client = AsyncSlamClient(server_adress, task_queue=self.send_queue, result_queue=self.receive_queue)
		self.image_to_send[np.ndarray,float].connect(self.send_image)
		self.trajectory_request.connect(self.request_trajectory)

	def send_image(self, img, timestamp):
		img_bytes = cv2.imencode('.jpg', img)[1].tostring()
		#print("Sending {}".format(timestamp))
		timestamp = bytes(struct.pack("d", timestamp))
		flag = bytes(struct.pack("c", b'a'))
		data = flag+timestamp+img_bytes
		self.send_queue.put(data, block=False)

	def request_trajectory(self):
		self.send_queue.put(b't\xff\xd8\xff\xd9')

	def run(self):
		while True:
			if not self.send_queue.empty():
				try:
					asyncore.loop(count=40)
					print('getting response')
				except asyncore.ExitNow:
					pass
			if not self.receive_queue.empty():
				data = self.receive_queue.get()
				if data == b'ok':
					self.image_response.emit(b'ok')
				else:
					self.trajectory_response.emit(data)
			QApplication.processEvents()