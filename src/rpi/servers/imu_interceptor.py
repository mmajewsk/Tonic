from __future__ import print_function # Only Python 2.x
import subprocess
import multiprocessing


class MultiImuSubprocess(multiprocessing.Process):
	def __init__(self, result_queue, death_pill_queue, cmd, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		self.result_queue = result_queue
		self.death_pill_queue=death_pill_queue
		self.data = None
		self.cmd = cmd

	def run(self):
		cmd = self.cmd
		popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
		for stdout_line in iter(popen.stdout.readline, ""):
			s = stdout_line
			self.data = [float(number) for number in s.split()]
			self.return_data()
			if not self.death_pill_queue.empty():
				break
		popen.stdout.close()
		return_code = popen.wait()
		if return_code:
			raise subprocess.CalledProcessError(return_code, cmd)


	def return_data(self):
		while not self.result_queue.empty():
			self.result_queue.get()
		self.result_queue.put(self.data)

class ImuEuler:
	def __init__(self):
		cmd = ["minimu9-ahrs",'--output','euler']
		self.result_queue = multiprocessing.Queue()
		self.death_pill_queue = multiprocessing.Queue()
		self.process = MultiImuSubprocess(self.result_queue, self.death_pill_queue, cmd)

	def connect(self):
		self.process.start()

	def read(self):
		data = self.result_queue.get()
		return data

	def __del__(self):
		self.death_pill_queue.put("kill")
		self.process.terminate()