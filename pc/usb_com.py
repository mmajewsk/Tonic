import serial

def keys_to_command(keys):
		w,s,a,d = 87,83,68,65
		keytab = map(lambda x: keys[x], (w,s,a,d))
		command = sum(1<<i for i, b in enumerate(keytab) if b)
		return command

class Steering(object):
	def __init__(self):
		self.ser = serial.Serial('COM3', 115200, timeout=1);

	def __enter__(self):
		pass

	def __exit__(self,type, value, traceback):
		self.close()

	def close(self):
		self.ser.close()

	def write_command(self, command):
		self.ser.write(bytes([command]))

	def write_keys(self, keys):
		self.write_command(keys_to_command(keys))

	def print(self):
		print(self.ser.readlines())





