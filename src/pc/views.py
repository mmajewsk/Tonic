from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from logic import logic_layers


class MainApp(QWidget):
	def __init__(self, controller, children=[]):
		QWidget.__init__(self)
		self.children = children
		self.controller = controller
		self.intake_path = None
		if self.controller.steering_client:
			self.keys = self.controller.steering_client.key_events()
			self.setup_steering()
		else:
			self.keys = {}
		if self.controller.video_client:
			self.setup_camera()
		self.setup_logic_pipeline()
		self.setup_ui()

	def setup_logic_pipeline(self):
		self.pipeline = logic_layers

	def setup_steering(self):
		self.keys[17] = False
		self.controller.connect_steering(self)

	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		if self.controller.video_client:
			size = self.controller.video_client.video_size
		else:
			size = (320,240)
		video_size = QSize(*size)
		self.image_label.setFixedSize(video_size)

		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close)

		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.main_layout.addWidget(self.quit_button)

		self.setLayout(self.main_layout)

	def setup_camera(self):
		"""Initialize camera.
		"""
		self.timer = QTimer()
		self.timer.timeout.connect(self.refresh_view)
		self.timer.start(60)
		self.controller.connect_video()

	def refresh_view(self):
		if self.controller.video_client:
			frame = self.controller.frame
			self.display_video_stream(frame)

	def display_video_stream(self, frame):
		image = QImage(frame, frame.shape[1], frame.shape[0],
					   frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))

	def keyPressEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_Control]:
			self.keys[event.key()] = True

	def keyReleaseEvent(self, event):
		if event.key() in [Qt.Key_W, Qt.Key_S, Qt.Key_A, Qt.Key_D, Qt.Key_Control]:
			self.keys[event.key()] = False

	def close(self):
		del self.controller
		if self.children:
			for child in self.children:
				child.close()
		QWidget.close(self)

class MapWindow(QWidget):
	def __init__(self, controller):
		QWidget.__init__(self)
		self.controller = controller
		self.setup_ui()
		self.setup_imu()

	def setup_ui(self):
		"""Initialize widgets.
		"""
		self.image_label = QLabel()
		video_size = QSize(320,240)
		self.image_label.setFixedSize(video_size)
		self.main_layout = QVBoxLayout()
		self.main_layout.addWidget(self.image_label)
		self.setLayout(self.main_layout)

	def refresh_view(self):
		text = "Acc:\n{}\nGyr:\n{}\nMag:\n{}"
		data = self.controller.data
		disp = text.format(data.acc, data.gyr, data.mag)
		self.image_label.setText(disp)

	def setup_imu(self):
		self.timer = QTimer()
		self.timer.timeout.connect(self.refresh_view)
		self.timer.start(60)
		self.controller.connect_imu()

	def close(self):
		self.controller.close()
		QWidget.close(self)