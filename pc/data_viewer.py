from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os, sys

import json
import time, datetime

class MainApp(QWidget):

	def __init__(self, data_path):
		QWidget.__init__(self)
		self.data_path = data_path
		self.dirlist = os.listdir(self.data_path)
		self.video_size = QSize(320, 240)
		self.setup_ui()
		self._current_dir = os.path.join(self.data_path, '')
		self.steering_hist = ''
		self.pic_list = []
		self.frame_list=[]
		self.frames = {}

	@property
	def current_dir(self):
		return self._current_dir

	@current_dir.setter
	def current_dir(self, newdir):
		self._current_dir = os.path.join(self.data_path, newdir.text())

	def load_frame(self, frame):
		image = QImage(os.path.join(self.current_dir, self.frames[frame][1]))
		self.image_label.setPixmap(QPixmap.fromImage(image))

	def create_frames(self, pic_list):
		self.frame_list = map(lambda x: x[5:-4].split('_'), pic_list)
		self.frame_list = map(lambda z: (int(z[0]), float(z[1])), self.frame_list)
		self.frames = {}
		for (number, t), pic in zip(self.frame_list, pic_list):
			self.frames[number] = (datetime.datetime.fromtimestamp(t), pic )



	def load_new_dir(self):
		dir_steering_path = os.path.join(self.current_dir,'steering.json')
		with open(dir_steering_path, 'r') as f:
			self.steering_hist = json.loads(f.read())
		self.pic_list = list(filter(lambda x: ".jpg" in x, os.listdir(self.current_dir)))
		self.create_frames(self.pic_list)
		self.slider.setMaximum(max(list(self.frames.keys())))
		self.load_frame(0)

	def on_dir_change(self, curr, prev):
		self.current_dir = curr
		self.load_new_dir()

	def change_frame(self, frame_number):
		self.load_frame(frame_number)
		frame = self.frames[frame_number]
		t = frame[0]
		tim = t.strftime("%H:%M:%S.%f")
		self.image_data.setText("Number:{} Time:{}".format(frame_number, tim))

	def setup_ui(self):
		self.image_label = QLabel()
		#self.image_label.setFixedSize(self.video_size)
		self.quit_button = QPushButton("Quit")
		self.quit_button.clicked.connect(self.close)

		self.main_layout = QHBoxLayout()
		self.image_layout = QVBoxLayout()
		self.image_layout.addWidget(self.image_label)
		self.image_data = QLabel()
		self.image_layout.addWidget(self.image_data)
		self.slider = QSlider(Qt.Horizontal)
		self.slider.setMinimum(0)
		self.slider.setTickInterval(1)
		self.slider.setMaximum(1)
		self.slider.valueChanged.connect(self.change_frame)
		self.image_layout.addWidget(self.slider)
		self.main_layout.addLayout(self.image_layout)
		self.file_list = QListWidget()
		self.file_list.addItems(self.dirlist)
		self.file_list.currentItemChanged.connect(self.on_dir_change)
		self.right_panel = QVBoxLayout()
		self.right_panel.addWidget(self.quit_button)
		self.right_panel.addWidget(self.file_list)
		self.main_layout.addLayout(self.right_panel)
		self.setLayout(self.main_layout)

	def display_video_stream(self):
		frame = self.frame
		image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
		self.image_label.setPixmap(QPixmap.fromImage(image))


if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainApp(sys.argv[1])
	win.show()
	sys.exit(app.exec_())



