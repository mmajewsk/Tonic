import asyncore
import logging
import sys; sys.path.append(".")
from server_management import BaseServer, BaseClientHandler, MasterLink
import json


class MasterClientHandler(BaseClientHandler):
	def __init__(self, master, sock, address):
		BaseClientHandler.__init__(self, sock, address)
		self.master = master

	def get_info(self, input_data):
		result_dict = {'status':{}}
		if not input_data:
			self.logger.error('Empty request')
			result_dict['info']="Empty request"
		try:
			raw_data = json.loads(input_data)
			data = raw_data['data']
			order = raw_data['order']
			result_dict['info'] = 'Ok'
			if order in ['start', 'stop', 'restart']:
				self.master.process_order(order, data)
			elif order == "status":
				status = self.master.get_status()
				if status is not None:
					print(status)
					print(type(status))
					result_dict['status'] = status
			else:
				result_dict['info'] = "Unknown Command"
		except Exception as e:
			self.logger.error('Exception occured"', e)
			result_dict['info'] = str(e)
		finally:
			return result_dict

	def readout(self, input_data):
		info = self.get_info(input_data)
		return info


class MasterServer(BaseServer):
	def __init__(self, address):
		BaseServer.__init__(self, address)
		self.master = MasterLink()
		self.master.process.start()

	def create_client(self, *args, **kwargs):
		return MasterClientHandler(self.master, *args, **kwargs)


def main():
	logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')
	HOST = ''
	PORT = 2205
	s = MasterServer((HOST, PORT))
	asyncore.loop()


if __name__ == '__main__':
	main()