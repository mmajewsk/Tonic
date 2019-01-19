#!/usr/bin/env python
''' Async TCP server to make first tests of newly received GPS trackers '''

import asyncore
import socket
import logging
import json
from imu_interceptor import ImuEuler

class ImuServer(asyncore.dispatcher):
	def __init__(self, address):
		asyncore.dispatcher.__init__(self)
		self.logger = logging.getLogger('Server')
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.address = self.socket.getsockname()
		self.logger.debug('binding to %s', self.address)
		self.listen(5)

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		if client_info is not None:
			self.logger.debug('handle_accept() -> %s', client_info[1])
			ImuClientHandler(client_info[0], client_info[1])


class ImuClientHandler(asyncore.dispatcher):
	def __init__(self, sock, address):
		asyncore.dispatcher.__init__(self, sock)
		self.logger = logging.getLogger('Client ' + str(address))
		self.data_to_write = []
		self.imu = ImuEuler()
		self.imu.connect()

	def writable(self):
		return bool(self.data_to_write)

	def handle_write(self):
		data = self.data_to_write.pop()
		sent = self.send(data[:1024])
		if sent < len(data):
			remaining = data[sent:]
			self.data_to_write.append(remaining)
		self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent].rstrip())

	def handle_read(self):
		data = self.recv(1024)
		self.logger.debug('handle_read() -> (%d) "%s"', len(data), data.rstrip())
		while True:
			imu_data = self.imu.read()
			if 'data' in imu_data:
				response = json.dumps(imu_data['data']).encode()
				self.data_to_write.insert(0, response)
				break
			elif 'info' in imu_data:
				self.logger.info(' ==========[{}]==========='.format(imu_data['info']))

	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()


def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2204
	s = ImuServer((HOST, PORT))
	asyncore.loop()


if __name__ == '__main__':
	main()
