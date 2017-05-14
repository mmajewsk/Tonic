import argparse
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os, sys
import pandas as pd
import json
import time, datetime

class MainApp(QWidget):

	def __init__(self, data_path, steering_file):
		QWidget.__init__(self)
		self.data_path = data_path
		self.dirlist = os.listdir(self.data_path)
		self.video_size = QSize(320, 240)
		self.setup_ui()
		self.painter = QPainter()
		self._current_dir = os.path.join(self.data_path, '')
		self.steering_hist = ''
		self.pic_list = []
		self.frame_list=[]
		self.frames = {}
		self.draw_border = 5
		self.steering_file = steering_file
		self.coord_draw = {
			'a': (self.draw_border, self.video_size.height()//2),
			'd': (self.video_size.width()-self.draw_border, self.video_size.height() // 2),
			'w': (self.video_size.width()//2, self.draw_border),
			's': (self.video_size.width()//2, self.video_size.height()-self.draw_border),
		}

	@property
	def current_dir(self):
		return self._current_dir

	@current_dir.setter
	def current_dir(self, newdir):
		self._current_dir = os.path.join(self.data_path, newdir.text())

	def draw_signals(self, frame, image):
		self.painter.begin(image)
		self.painter.setPen(Qt.red)
		self.painter.setBrush(QBrush(Qt.red))
		for	signal in "wsad":
			if frame[signal]:
				x,y = self.coord_draw[signal]
				self.painter.drawEllipse(x,y, 10, 10)
		self.painter.end()
		return image

	def load_frame(self, frame_number):
		frame = self.frames[frame_number]
		image = QImage(os.path.join(self.current_dir, frame['filenames']))
		image = self.draw_signals(frame, image)
		self.image_label.setPixmap(QPixmap.fromImage(image))

	@staticmethod
	def to_common_datatype(df):
		frames = {}
		for i, (index , data) in enumerate(df.to_dict('index').items()):
			frames[i] = dict(date=datetime.datetime.fromtimestamp(index), **data)
		return frames

	def create_frames(self):
		self.frames = self.to_common_datatype(self.data)

	def load_new_dir(self):
		dir_steering_path = os.path.join(self.current_dir,self.steering_file)
		self.data = pd.read_csv(dir_steering_path)
		self.create_frames()
		self.slider.setMaximum(max(list(self.frames.keys())))
		self.load_frame(0)

	def on_dir_change(self, curr, prev):
		self.current_dir = curr
		self.load_new_dir()

	def change_frame(self, frame_number):
		self.load_frame(frame_number)
		frame = self.frames[frame_number]
		t = frame['date']
		tim = t.strftime("%H:%M:%S.%f")
		signal = "".join([k if frame[k]==True else '' for k in "wsad"])
		self.image_data.setText("Number:{} Time:{} \n Signal:{}".format(frame_number, tim, signal))

	def setup_ui(self):
		self.image_label = QLabel()
		self.image_label.setFixedSize(self.video_size)
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
	parser = argparse.ArgumentParser(description='View the data')
	parser.add_argument('folder', type=str)
	parser.add_argument('--steering_file', metavar='steering_file', type=str, default='steering_v1.csv',
						help='name of the file to use to reconstruct the steering signal')

	args = parser.parse_args()
	app = QApplication(sys.argv)
	win = MainApp(args.folder, args.steering_file)
	win.show()
	sys.exit(app.exec_())



