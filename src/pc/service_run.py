import yaml
import argparse
import json
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from clients.master_client import QTMasterClient
from PyQt5.QtCore import pyqtSignal

class ServerConnection(QGroupBox):
	status = pyqtSignal(str)

	def __init__(self, master_client: QTMasterClient, name, command):
		QGroupBox.__init__(self, name)
		self.name = name
		self.command = command
		self.master_client = master_client
		self.data = dict(name=self.name, command=self.command)
		self.start_time = None
		self.create_ui()
		self.connect_signal()

	def connect_signal(self):
		self.status[str].connect(self.update_status)

	def process_status_response(self, response):
		status_message = None
		status_time = None
		try:
			status_time = datetime.datetime.strptime(response, '%Y-%m-%d %H:%M:%S.%f')
			status_message = "Ok"
		except:
			status_message = response
		return status_message, status_time


	def update_status(self, _status):
		status_message, status_time = self.process_status_response(_status)
		self.status_message = status_message
		if status_time is not None:
			#print(self.start_time, status_time)
			if self.start_time is None:
				self.start_time = status_time
			self.time_elapsed = (status_time-self.start_time).total_seconds()
		else:
			self.time_elapsed = 0
		self.time_elapsed_label.setText(str(self.time_elapsed))
		self.status_label.setText(self.status_message)

	def	start(self):
		request = dict(order='start',data=self.data)
		#self.start_time = datetime.datetime.now()
		self.master_client.request[dict].emit(request)

	def stop(self):
		request = dict(order='stop', data=self.data)
		self.master_client.request[dict].emit(request)
		self.start_time = None

	def restart(self):
		request = dict(order='restart', data=self.data)
		self.master_client.request[dict].emit(request)
		self.start_time = None


	def create_ui(self):
		layout = QHBoxLayout()

		self.command_text = QLabel(self)
		self.command_text.setText(self.command)
		layout.addWidget(self.command_text)

		button_start = QPushButton('start', self)
		button_start.clicked.connect(self.start)
		layout.addWidget(button_start)

		button_stop = QPushButton('stop', self)
		button_stop.clicked.connect(self.stop)
		layout.addWidget(button_stop)

		button_restart = QPushButton('restart', self)
		button_restart.clicked.connect(self.restart)
		layout.addWidget(button_restart)

		self.status_label = QLabel(self)
		self.status_label.setText("status")
		layout.addWidget(self.status_label)

		self.time_elapsed_label = QLabel(self)
		self.time_elapsed_label.setText("0")
		layout.addWidget(self.time_elapsed_label)

		self.setLayout(layout)


class App(QDialog):
	def __init__(self, settings_dict):
		super().__init__()
		self.title = 'Server watch'
		self.left = 10
		self.top = 10
		self.width = 320
		self.height = 100
		ip = settings_dict.pop('ip')
		master_port = settings_dict.pop('master')['port']
		self.settings = settings_dict
		self.server_client = QTMasterClient((ip,master_port), verbose=True)
		self.initUI()
		self.server_client.status[dict].connect(self.status_change)


	def status_change(self, status):
		self.info_label.setText(status['info'])
		for name, server_status in status['status'].items():
			self.server_connections[name].status.emit(server_status)

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.info_label = QLabel(self)
		self.info_label.setText("Info")
		self.server_connections = {}
		for server, settings in self.settings.items():
			if 'command' in settings:
				self.server_connections[server] = ServerConnection(self.server_client, name=server, command=settings['command'])
		windowLayout = QVBoxLayout()
		windowLayout.addWidget(self.info_label)
		for server_connection in self.server_connections.values():
			windowLayout.addWidget(server_connection)
		self.setLayout(windowLayout)
		self.show()

def read_settibngs_to_dict(settings_path):
	settings = yaml.load(open(settings_path, 'rb'))
	return settings['server']

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('--settings', dest='settings_file', type=str, default=None,
						help='path to settings file')
	args = parser.parse_args()
	settings_dict = read_settibngs_to_dict(args.settings_file)
	app = QApplication(['service_run'])
	ex = App(settings_dict)
	sys.exit(app.exec_())