import numpy as np
import cv2
import socket

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import sys

from usb_com import Steering


class GetCameraImage(QThread):
	image_downloaded = pyqtSignal(np.ndarray)

	def __init__ (self):
		QThread.__init__(self)
		self.client_socket = None
		self.binary_stream = None
		self.client_socket = socket.socket()
		host = '192.168.1.212' # - local
		#host = 'masterday.hopto.org'
		self.client_socket.connect((host,2201))
		self.binary_stream = self.client_socket.makefile('rb')
		self.payload = b' '

	def __del__(self):
		if self.binary_stream is not None:
			self.binary_stream.close()
		if self.client_socket is not None:
			self.client_socket.close()

	def run(self):
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
				frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
				frame = cv2.flip(frame, 1)
				frame = cv2.flip(frame, 0)
				self.image_downloaded.emit(frame)
				
				#return image
        


class MainApp(QWidget):

	def __init__(self):
		QWidget.__init__(self)
		self.video_size = QSize(640, 480)
		self.setup_steering()
		self.setup_ui()
		self.setup_camera()

	def setup_steering(self, create_timer=True):
		self.keys = {65: False, 83: False, 68: False, 87: False}#asdw
		self.steering = None
		if create_timer:
			self.steering = Steering()
			self.timer2 = QTimer()
			self.timer2.timeout.connect(self.stream_steering)
			self.timer2.start(30)


	def stream_steering(self):
		#print(self.keys)
		self.steering.write_keys(self.keys)


	def __del__(self):
		self.close()

	def close(self):
		if self.steering is not None:
			self.steering.close() 


	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		self.image_label.setFixedSize(self.video_size)

		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close)

		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.main_layout.addWidget(self.quit_button)

		self.setLayout(self.main_layout)

	def setup_camera(self):
		"""Initialize camera.
		"""
		self.frame = np.zeros((10,10,3))
		self.thread = QThread()
		self.get_camera = GetCameraImage()
		self.get_camera.image_downloaded[np.ndarray].connect(self.add_image)
		self.get_camera.moveToThread(self.thread)
		self.timer = QTimer()
		self.timer.timeout.connect(self.display_video_stream)
		self.timer.start(30)
		self.get_camera.start()

	def add_image(self, frame):
		self.frame = frame

	def display_video_stream(self):
		frame = self.frame
		image = QImage(frame, frame.shape[1], frame.shape[0], 
					   frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))

	def keyPressEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
			self.keys[event.key()] = True
		

	def keyReleaseEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D]:
			self.keys[event.key()] = False



if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainApp()
	win.show()
	sys.exit(app.exec_())



