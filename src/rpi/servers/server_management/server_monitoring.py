import time
import multiprocessing
import datetime
import subprocess
from abc import ABCMeta, abstractmethod
import os

class Guard(multiprocessing.Process):
	def __init__(self, cmd, input_queue, output_queue, **kwargs):
		multiprocessing.Process.__init__(self, **kwargs)
		self.cmd = cmd
		self.input_queue = input_queue
		self.output_queue = output_queue
		self.go = False

	def is_alive(self):
		date = datetime.datetime.now()
		self.output_queue.put(str(date))

	def died(self, rcode):
		if rcode:
			self.output_queue.put("Death " + str(rcode))
		else:
			self.output_queue.put("Death")

	def process_order(self):
		if not self.input_queue.empty():
			order = self.input_queue.get()
			if order == "serve":
				self.go = True
			elif order == "kill":
				self.go = False

	def run(self):
		while True:
			self.process_order()
			return_code = ""
			if self.go:
				try:
					popen = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, universal_newlines=True, cwd=os.getcwd(), shell=True)
					for stdout_line in iter(popen.stdout.readline, ""):
						s = stdout_line
						self.is_alive()
						self.process_order()
						if self.go == False:
							break
					self.go = False
					# @TODO CLOSE IF FORCED!!!
					popen.stdout.close()
					# return_code = popen.wait()
					popen.kill()
				except Exception as e:
					return_code = str(e)
				self.died(return_code)
			time.sleep(1)

class ProcessLink:
	__metaclass__ = ABCMeta

	def __init__(self, *args, **kwargs):
		self.input_queue = multiprocessing.Queue()
		self.output_queue = multiprocessing.Queue()
		self.process = self.create_process(*args, **kwargs)

	@abstractmethod
	def create_process(self, *args, **kwargs):
		pass

	def __del__(self):
		if not self.process is None:
			self.process.terminate()
			self.process.join()


class GuardLink(ProcessLink):
	def __init__(self, name, command, **kwargs):
		ProcessLink.__init__(self, command=command)
		self.name = name

	def create_process(self, command):
		return Guard(command, self.input_queue, self.output_queue)

	@property
	def status(self):
		_status = None
		while not self.output_queue.empty():
			_status = self.output_queue.get()
		return _status

	def start(self):
		self.input_queue.put("serve")

	def stop(self):
		self.input_queue.put("kill")

	def __del__(self):
		self.stop()
		ProcessLink.__del__(self)


class Master(multiprocessing.Process):
	def __init__(self, input_queue, output_queue, dt=1.):
		multiprocessing.Process.__init__(self)
		self.dt=dt
		self.input_queue = input_queue
		self.output_queue = output_queue
		self.guards = {}
		self.status = {}

	def start_guard(self, data):
		if not data['name'] in self.guards.keys():
			self.guards[data['name']] = GuardLink(**data)
		self.guards[data['name']].process.start()
		self.guards[data['name']].start()

	def stop_guard(self, data):
		self.guards[data['name']].stop()

	def restart_guard(self, data):
		del self.guards[data['name']]
		self.start_guard(data)

	# (order, data)
	# order=='start'
	# data = {'name': 'servicename', 'command':'python server__.py 193124.435'}

	def process_order(self):
		if not self.input_queue.empty():
			order, data = self.input_queue.get_nowait()
			if order == "start":
				self.start_guard(data)
			elif order == "stop":
				self.stop_guard(data)
			elif order == "restart":
				self.restart_guard(data)
			elif order == "status":
				self.output_queue.put(self.status)

	def run(self):
		while True:
			self.process_order()
			for name, guard_link in self.guards.items():
				self.status[name] = self.guards[name].status
			time.sleep(self.dt)
			self.process_order()

class MasterLink(ProcessLink):
	def __init__(self):
		ProcessLink.__init__(self)

	def create_process(self, *args, **kwargs):
		return Master(self.input_queue, self.output_queue)

	def process_order(self, order, data):
		self.input_queue.put((order, data))

	def get_status(self):
		self.input_queue.put(("status", None))
		status = None
		while not self.output_queue.empty():
			status = self.output_queue.get()
		return status