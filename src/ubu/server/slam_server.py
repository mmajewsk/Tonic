#!/usr/bin/env python
''' Async TCP server to make first tests of newly received GPS trackers '''

import asyncore
import socket
import logging
import json
from slam_manager import SlamManager

class Server(asyncore.dispatcher):
	def __init__(self, address):
		asyncore.dispatcher.__init__(self)
		self.logger = logging.getLogger('Server')
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(address)
		self.address = self.socket.getsockname()
		self.logger.debug('binding to %s', self.address)
		self.listen(5)
		self.slam_manager=SlamManager()

	def handle_accept(self):
		# Called when a client connects to our socket
		client_info = self.accept()
		if client_info is not None:
			self.logger.debug('handle_accept() -> %s', client_info[1])
			ClientHandler(client_info[0], client_info[1], slam_manager=self.slam_manager)


class ClientHandler(asyncore.dispatcher):
	def __init__(self, sock, address, slam_manager):
		asyncore.dispatcher.__init__(self, sock)
		self.logger = logging.getLogger('Client ' + str(address))
		self.data_to_write = []
		self.slam_manager = slam_manager
		self.data_buffer = ''

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
		part_data = self.recv(1024)
		self.data_buffer += part_data
		#print("part",part_data)
		#print('part_data {}'.format(part_data))
		first = self.data_buffer.find('\xff\xd8')
		last = self.data_buffer.find('\xff\xd9')
		if first != -1 and last != -1:
			#print(self.data_buffer[first],self.data_buffer[last])
			data = self.data_buffer[:last+2]
			print(first,last)
			print(data[:10],data[-10:] )
			self.data_buffer = self.data_buffer[last+2:]
			result = self.slam_manager.process(data)
			self.data_to_write.insert(0, result)
			self.logger.debug('handle_read() -> (%d) "%s"', len(data), data[:7])

	def handle_close(self):
		self.logger.debug('handle_close()')
		self.close()


def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2207
	s = Server((HOST, PORT))
	asyncore.loop()


if __name__ == '__main__':
	main()