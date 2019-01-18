import subprocess
import multiprocessing
from interruptingcow import timeout

class MultiImuSubprocess(multiprocessing.Process):
	def __init__(self, result_queue, death_pill_queue, cmd, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		self.result_queue = result_queue
		self.death_pill_queue=death_pill_queue
		self.data = None
		self.cmd = cmd

	def run(self):
		while True:
			cmd = self.cmd
			popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
			exit_really = False
			try:
				iterator = iter(popen.stdout.readline, "")
				while True:
					with timeout(0.8, exception=RuntimeError):
						stdout_line = next(iterator)
					s = stdout_line
					self.data = {'data': [float(number) for number in s.split()]}
					self.return_data()
					if not self.death_pill_queue.empty():
						exit_really = True
						break
			except RuntimeError:
				self.data = {'info': "Minimu response timeout"}
				self.return_data()
			popen.stdout.close()
			if exit_really:
				return_code = popen.wait()
				break
			popen.kill()
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
		data = {}
		if self.result_queue.empty():
			data = self.result_queue.get()
		return data

	def __del__(self):
		self.death_pill_queue.put("kill")
		self.process.terminate()
