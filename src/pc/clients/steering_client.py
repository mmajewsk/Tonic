from PyQt5.QtCore import QThread, QTimer
import socket
import time
import os
import json

class QTSteeringClient(QThread):
	to_letters_dict = {87:'w', 83:'s', 68:'d', 65:'a'}
	to_numbers_dict = {'w':87, 's':83, 'd':68, 'a':65}
	wsad_int = [87, 83, 65, 68]


	@staticmethod
	def key_events():
		return {65: False, 83: False, 68: False, 87: False}

	@staticmethod
	def letter_to_numbers(d):
		return {QTSteeringClient.to_numbers_dict[k]: v for k, v in d.items()}

	def __init__(self, server_adress, verbose=True):
		self.controller = None
		QThread.__init__(self)
		self.server_adress = server_adress
		if verbose:
			print("Connecting to {}".format(server_adress))
		self.socket = socket.socket()
		self.socket.connect(server_adress)
		self.steering_log = []

	def connect_controller(self, controller):
		self.controller = controller
		self.timer2 = QTimer()
		self.timer2.timeout.connect(self.ask_keys)
		self.timer2.start(28)

	def ask_keys(self):
		self.send(self.controller.keys)

	def signal_to_string(self, signal):
		rval = " "
		for key in self.key_events():
			if signal[key]:
				rval += self.to_letters_dict[key]
		return rval

	def send(self, keys):
		signal = self.signal_to_string(keys)
		self.socket.send(signal.encode())
		self.steering_log.append((dict(keys), time.time()))

	def dump_log(self, dumpath):
		with open(os.path.join(dumpath,'steering.json'), 'w') as f:
			f.write(json.dumps(self.steering_log))

	def __del__(self):
		self.socket.close()


