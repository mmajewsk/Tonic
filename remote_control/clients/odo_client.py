from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from abc import ABCMeta, abstractmethod
import multiprocessing
import time
import json
from clients import Client
import queue

class OdoClient(Client):
	__metaclass__ =ABCMeta

	def __init__(self, server_adress=('192.168.1.239',2204), dt=0.1, connect=False):
		super(OdoClient, self).__init__(server_adress, connect)
		self.dt = dt

	def run(self):
		finished = True
		result = None
		data = ''
		while True:
			if finished:
				self.client_socket.send(b' ')
				data = self.client_socket.recv(1024).decode()
			else:
				data += self.client_socket.recv(1024).decode()
			try:
				result = json.loads(data)
			except json.decoder.JSONDecodeError as e:
				finished = False
			else:
				finished = True
				self.return_data(result)
				time.sleep(self.dt),


class MultiOdoClient(OdoClient, multiprocessing.Process):
	def __init__(self, task_queue, result_queue, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		OdoClient.__init__(self, *args, **kwargs)
		self.task_queue = task_queue
		self.result_queue = result_queue

	def run(self):
		self.connect()
		OdoClient.run(self)

	def return_data(self, frame):
		_ = self.task_queue.get()
		self.task_queue.task_done()
		self.result_queue.put(frame)
		time.sleep(self.dt)



class QTOdoClient(OdoClient, QThread):
	data_downloaded = pyqtSignal(dict)
	def __init__(self, *args, **kwargs):
		QThread.__init__(self)
		OdoClient.__init__(self, *args, **kwargs)

	def __enter__(self):
		self.connect()

	def __exit__(self, type, value, traceback):
		self.__del__()

	def return_data(self, frame):
		self.data_downloaded.emit(frame)



class OdoWorker:
	def __init__(self, *args, **kwargs):
		manager = multiprocessing.Manager()
		self.r = manager.Queue()
		self.t = manager.Queue()
		self.client = MultiOdoClient(self.t, self.r, *args, **kwargs)
		self.client.start()

	def read(self):
		self.t.put('')
		return self.r.get()

if __name__=='__main__':
	server_adress = ('192.168.1.98', 2206)
	w = OdoWorker(server_adress=server_adress, dt=0.5)
	while True:
		print(w.read())
		print("----")
