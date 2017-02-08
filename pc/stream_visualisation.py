import numpy as np
import cv2
import socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import sys

class MainApp(QWidget):

	def __init__(self):
		QWidget.__init__(self)
		self.video_size = QSize(640, 480)
		self.setup_ui()
		self.setup_camera()

	def close_disconnect(self):
		self.binary_stream.close()
		self.client_socket.close()
		self.close()

	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		self.image_label.setFixedSize(self.video_size)

		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close_disconnect)

		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.main_layout.addWidget(self.quit_button)

		self.setLayout(self.main_layout)

	def setup_camera(self):
		"""Initialize camera.
		"""
		self.client_socket = socket.socket()
		host = '192.168.1.212' # - local
		#host = 'masterday.hopto.org'
		self.client_socket.connect((host,2201))
		self.binary_stream = self.client_socket.makefile('rb')
		self.payload = b' '


		self.timer = QTimer()
		self.timer.timeout.connect(self.display_video_stream)
		self.timer.start(30)

	def download_image(self):
		broadcast = True
		frame = 1
		image_start = b'\xff\xd8'
		image_end = b'\xff\xd9'

		while broadcast:
			self.payload += self.binary_stream.read(1024)
			first = self.payload.find(image_start)
			last = self.payload.find(image_end)
			if first != -1 and last != -1:
				self.jpg = self.payload[first:last + 2]
				self.payload = self.payload[last + 2:]
				image = cv2.imdecode(np.fromstring(self.jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
				return image

	def display_video_stream(self):
		frame = self.download_image()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = cv2.flip(frame, 1)
		image = QImage(frame, frame.shape[1], frame.shape[0], 
					   frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))



if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainApp()
	win.show()
	sys.exit(app.exec_())



