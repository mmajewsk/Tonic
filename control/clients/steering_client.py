from PyQt5.QtCore import QThread, QTimer
import socket
import time
import os
import json
from clients import Client

class MotorClient(Client):
	def __init__(self, server_adress, connect):
		Client.__init__(self, server_adress, connect)
		self.steering_log = []

	def send(self, input):
		signal = self.signal_to_string(input)
		print("blorgoooooo")
		self.client_socket.send(signal.encode())
		self.steering_log.append((input, time.time()))

	def return_data(self, frame):
		pass

	def dump_log(self, dumpath):
		with open(os.path.join(dumpath,'steering.json'), 'w') as f:
			f.write(json.dumps(self.steering_log))

	def ask_input(self):
		if self.controller.steering_commands is not None:
			self.send(self.controller.steering_commands)

	def signal_to_string(self, signal):
		return json.dumps(signal)+"br"

	def run(self):
		pass

class QTBaseSteering(QThread):
	def __init__(self, server_adress, verbose=True):
		self.controller = None
		QThread.__init__(self)
		self.server_adress = server_adress
		if verbose:
			print("Connecting to {}".format(server_adress))
		self.socket = socket.socket()
		self.socket.connect(server_adress)
		self.steering_log = []
		self.timer_frequency = 28

	def connect_controller(self, controller):
		self.controller = controller
		self.timer2 = QTimer()
		self.timer2.timeout.connect(self.ask_input)
		self.timer2.start(self.timer_frequency)

	def ask_input(self):
		pass

	def signal_to_string(self, signal):
		pass

	def send(self, input):
		signal = self.signal_to_string(input)
		self.socket.send(signal.encode())
		self.steering_log.append((input, time.time()))


	def __del__(self):
		self.socket.close()


class QTSteeringClient(QTBaseSteering):
	to_letters_dict = {87:'w', 83:'s', 68:'d', 65:'a'}
	to_numbers_dict = {'w':87, 's':83, 'd':68, 'a':65}
	wsad_int = [87, 83, 65, 68]

	@staticmethod
	def key_events():
		return {65: False, 83: False, 68: False, 87: False}

	@staticmethod
	def letter_to_numbers(d):
		return {QTSteeringClient.to_numbers_dict[k]: v for k, v in d.items()}

	def ask_input(self):
		self.send(self.controller.keys)

	def signal_to_string(self, signal):
		rval = " "
		for key in self.key_events():
			if signal[key]:
				rval += self.to_letters_dict[key]
		return rval

	def dump_log(self, dumpath):
		with open(os.path.join(dumpath,'steering.json'), 'w') as f:
			f.write(json.dumps(self.steering_log))



class QTSteeringMotor(QTBaseSteering):

	def ask_input(self):
		if self.controller.steering_commands is not None:
			self.send(self.controller.steering_commands)

	def signal_to_string(self, signal):
		return json.dumps(signal)
