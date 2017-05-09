from PyQt5.QtCore import QThread, QTimer
import socket
import time
import os
import json

class SetSteering(QThread):

	@staticmethod
	def key_events():
		return {65: False, 83: False, 68: False, 87: False}

	def __init__(self, app, server_adress, intake_path=None, dump=True, turn_on=True, verbose=True):
		self.intake_path = intake_path
		self.dump = dump
		self.app = app
		QThread.__init__(self)
		self.server_adress = server_adress
		if verbose:
			print("Connecting to {}".format(server_adress))
		self.socket = socket.socket()
		self.socket.connect(server_adress)
		self.steering_log = []
		self.to_letters_dict = {87:'w', 83:'s', 68:'d', 65:'a'}
		self.steering = turn_on
		if self.steering:
			self.timer2 = QTimer()
			self.timer2.timeout.connect(self.ask_keys)
			self.timer2.start(28)

	def ask_keys(self):
		self.send(self.app.keys)

	def signal_to_string(self, signal):
		rval = " "
		for key in signal:
			if signal[key]:
				rval += self.to_letters_dict[key]
		return rval

	def send(self, keys):
		signal = self.signal_to_string(keys)
		self.socket.send(signal.encode())
		self.steering_log.append((dict(keys), time.time()))

	def dump_log(self):
		if self.dump is True:
			with open(os.path.join(self.intake_path,'steering.json'), 'w') as f:
				f.write(json.dumps(self.steering_log))

	def __del__(self):
		if self.steering is not None:
			self.socket.close()


