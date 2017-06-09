from abc import ABCMeta, abstractmethod
import socket
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

class Client:
	__metaclass__ =ABCMeta

	def __init__(self, server_adress, connect=False):
		self.client_socket = None
		self.binary_stream = None
		self.client_socket = None
		self.server_adress = server_adress
		if connect:
			self.connect()

	def connect(self):
		self.client_socket = socket.socket()
		self.client_socket.connect(self.server_adress)

	@abstractmethod
	def return_data(self, frame):
		pass

	@abstractmethod
	def run(self):
		pass

	def __del__(self):
		if self.client_socket is not None:
			self.client_socket.close()