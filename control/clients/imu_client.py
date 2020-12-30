from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from abc import ABCMeta, abstractmethod
import multiprocessing
import time
import json
from clients import Client
import queue

class ImuClient(Client):
	__metaclass__ =ABCMeta

	def __init__(self, server_adress=('192.168.1.239',2204), dt=0.1, connect=False):
		super(ImuClient, self).__init__(server_adress, connect)
		self.dt = dt

	def run(self):
		while True:
			self.client_socket.send(b' ')
			data = self.client_socket.recv(1024).decode()
			result = json.loads(data)
			result = np.array(result, float)
			self.return_data(result)
			time.sleep(self.dt)


class MultiImuClient(ImuClient, multiprocessing.Process):
	def __init__(self, task_queue, result_queue, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		ImuClient.__init__(self, *args, **kwargs)
		self.task_queue = task_queue
		self.result_queue = result_queue

	def run(self):
		self.connect()
		ImuClient.run(self)

	def return_data(self, frame):
		_ = self.task_queue.get()
		self.task_queue.task_done()
		self.result_queue.put(frame)
		time.sleep(self.dt)



class QTImuClient(ImuClient, QThread):
	data_downloaded = pyqtSignal(np.ndarray)
	def __init__(self, *args, **kwargs):
		QThread.__init__(self)
		ImuClient.__init__(self, *args, **kwargs)

	def __enter__(self):
		self.connect()

	def __exit__(self, type, value, traceback):
		self.__del__()

	def return_data(self, frame):
		self.data_downloaded.emit(frame)



class ImuWorker:
	def __init__(self, *args, **kwargs):
		manager = multiprocessing.Manager()
		self.r = manager.Queue()
		self.t = manager.Queue()
		self.client = MultiImuClient(self.t, self.r, *args, **kwargs)
		self.client.start()

	def read(self):
		self.t.put('')
		return self.r.get()

if __name__=='__main__':
	server_adress = ('192.168.1.239', 2204)
	w = ImuWorker(server_adress=server_adress, dt=0.5)
	while True:
		print(w.read())
		print("----")
