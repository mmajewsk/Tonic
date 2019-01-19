import json
import multiprocessing
import RPi.GPIO as GPIO
import time
import datetime
from server_management import BaseServer, BaseClientHandler, ProcessLink
import logging
import asyncore

class Odometer:
	def __init__(self, input_pin):
		self.input_pin = input_pin
		GPIO.setup(input_pin, GPIO.IN)
		self.prevous_state = self.status
		self._history = []

	@property
	def status(self):
		return GPIO.input(self.input_pin)

	def	check_slope(self):
		status = self.status
		if self.prevous_state != status:
			self._history.append((status, str(datetime.datetime.now())))
			self.prevous_state = status

	@property
	def history(self):
		tmp = list(self._history)
		self._history = []
		return tmp

class OdoSystem(multiprocessing.Process):
	def __init__(self, left_pin, right_pin, input_queue, output_queue, dt=0.05):
		multiprocessing.Process.__init__(self)
		self.dt=dt
		self.runnable = True
		self.input_queue=input_queue
		self.output_queue=output_queue
		GPIO.setmode(GPIO.BCM)
		self.left = Odometer(left_pin)
		self.right = Odometer(right_pin)
		self._data = {}

	def update(self):
		self.left.check_slope()
		self.right.check_slope()

	def process_command(self):
		while not self.input_queue.empty():
			command = self.input_queue.get()
			if command == "kill":
				self.runnable=False
			elif command == "read":
				self.output_queue.put(self.data)
	@property
	def data(self):
		return dict(left=self.left.history, right=self.right.history)

	def run(self):
		while self.runnable:
			for i in range(10):
				time.sleep(self.dt)
				self.update()
			self.process_command()


class OdoLink(ProcessLink):

	def __init__(self, left_pin, right_pin, dt):
		self.left_pin=left_pin
		self.right_pin=right_pin
		self.dt=dt
		ProcessLink.__init__(self)

	def create_process(self):
		return OdoSystem(self.left_pin, self.right_pin, self.input_queue, self.output_queue, dt=self.dt)

	def start(self):
		self.process.start()

	def read(self):
		self.input_queue.put("read")
		readout = dict(left=[],right=[])
		while not self.output_queue.empty():
			readout = self.output_queue.get()
		return readout


	def stop(self):
		self.input_queue.put("kill")

	def __del__(self):
		self.stop()
		ProcessLink.__del__(self)


class OdoClientHandler(BaseClientHandler):
	def __init__(self, sock, address, odo, jsonify=True):
		BaseClientHandler.__init__(self, sock, address, jsonify=jsonify)
		self.odo=odo

	def readout(self, input_data):
		return self.odo.read()


class OdoServer(BaseServer):
	def __init__(self,pins, address, dt=0.05):
		BaseServer.__init__(self, address)
		self.odo = OdoLink(pins[0], pins[1], dt)
		self.odo.start()
		time.sleep(5)

	def create_client(self, *args, **kwargs):
		return OdoClientHandler(*args, odo=self.odo, **kwargs)

def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2206
	s = OdoServer((12,16), (HOST, PORT), dt=0.01)
	asyncore.loop()


if __name__ == '__main__':
	main()