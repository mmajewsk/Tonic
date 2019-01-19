import socket
import json
from abc import ABCMeta, abstractmethod
import asyncore
import logging

class BaseServer(asyncore.dispatcher):
	__metaclass__ = ABCMeta

	def __init__(self, address):
		asyncore.dispatcher.__init__(self)
		classname = type(self).__name__
		self.logger = logging.getLogger(classname)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.address = self.socket.getsockname()
		self.logger.debug('binding to %s', self.address)
		self.listen(5)

	@abstractmethod
	def create_client(self, *args, **kwargs):
		pass

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		if client_info is not None:
			self.logger.debug('handle_accept() -> %s', client_info[1])
			self.create_client(client_info[0], client_info[1])


class BaseClientHandler(asyncore.dispatcher):
	__metaclass__ = ABCMeta

	def __init__(self, sock, address, jsonify=False):
		asyncore.dispatcher.__init__(self, sock)
		classname = type(self).__name__
		self.logger = logging.getLogger(classname + ' ' + str(address))
		self.data_to_write = []
		self.jsonify_output = jsonify


	def writable(self):
		return bool(self.data_to_write)

	def handle_write(self):
		data = self.data_to_write.pop()
		sent = self.send(data[:1024])
		if sent < len(data):
			remaining = data[sent:]
			self.data_to_write.append(remaining)
		self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

	@abstractmethod
	def readout(self, input_data):
		pass

	def handle_read(self):
		data = self.recv(1024)
		input_data = data.rstrip()
		self.logger.debug('handle_read() -> (%d) "%s"', len(input_data), input_data.rstrip())
		readout = self.readout(input_data.decode())
		if self.jsonify_output:
			response = json.dumps(readout).encode()
		else:
			response = readout
		self.data_to_write.insert(0, response)

	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()

def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2204
	s = Server((HOST, PORT))
	asyncore.loop()
