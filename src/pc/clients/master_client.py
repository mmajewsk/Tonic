from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import json
from clients import Client



class QTMasterClient(Client, QThread):
	status = pyqtSignal(dict)
	request = pyqtSignal(dict)

	#On request change signa

	def __init__(self, server_adress, verbose=False):
		QThread.__init__(self)
		Client.__init__(self, server_adress)
		if verbose:
			print("Connecting to {}".format(server_adress))
		self.connect()
		self.connect_status()
		self.request.connect(self.send_request)

	def check_status(self):
		self.send_request(dict(order="status",data=None))

	def get_status(self):
		data = self.client_socket.recv(1024).decode()
		data = json.loads(data)
		print(data)
		print(type(data))
		self.status.emit(data)

	def connect_status(self):
		self.timer1 = QTimer()
		self.timer1.timeout.connect(self.check_status)
		self.timer1.start(1000)

	def send_request(self, request):
		print("Request: [{}]".format(request))
		self.client_socket.send(json.dumps(request).encode())
		self.get_status()


	def __enter__(self):
		self.connect()

	def __exit__(self, type, value, traceback):
		self.__del__()

	def __del__(self):
		Client.__del__(self)

