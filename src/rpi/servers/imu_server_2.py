#!/usr/bin/env python
''' Async TCP server to make first tests of newly received GPS trackers '''

import asyncore
import socket
import logging
import json
from base_server import BaseServer, BaseClientHandler
from imu_interceptor import ImuEuler


class ImuClientHandler(BaseClientHandler):
	def __init__(self, sock, address):
		BaseClientHandler.__init__(self, sock, address)
		self.imu = ImuEuler()
		self.imu.connect()

	def readout(self, input_data):
		return self.imu.read()


class ImuServer(BaseServer):
	def __init__(self, address):
		BaseServer.__init__(self, address)

	def create_client(self, *args, **kwargs):
		return ImuClientHandler(*args, **kwargs)



def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2206
	s = ImuServer((HOST, PORT))
	asyncore.loop()


if __name__ == '__main__':
	main()