import argparse
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os, sys
import pandas as pd
import json
import time, datetime
from logic import SignalPainter
import cv2
from clients import QTSteeringClient

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
        self.signal_list=[]
        self.signal = {}
        self.draw_border = 5
        self.steering_file = steering_file
        self.signal_painter = SignalPainter(
            video_size= (320, 240),
            draw_border=self.draw_border,
            letters='wsad',
        )


    @property
    def current_dir(self):
        return self._current_dir

    @current_dir.setter
    def current_dir(self, newdir):
        self._current_dir = os.path.join(self.data_path, newdir.text())

    def draw_keys(self, *args, **kwargs):
        img, kwrgs = self.signal_painter.action(*args, **kwargs)
        return img

    def load_signal(self, signal_number):
        signal = self.signal[signal_number]
        picpath = os.path.join(self.current_dir, signal['filenames'])
        frame = cv2.imread(picpath)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = self.draw_keys(frame, keys=signal['keys'])
        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(image))

    @staticmethod
    def to_common_datatype(df):
        signal = {}
        for i, (index , data) in enumerate(df.to_dict('index').items()):
            keys = {k:data[k] for k in 'wsad'}
            signal[i] = dict(date=datetime.datetime.fromtimestamp(index), keys=keys, **data)
        return signal

    def create_signal(self):
        self.signal = self.to_common_datatype(self.data)

    def load_new_dir(self):
        dir_steering_path = os.path.join(self.current_dir,self.steering_file)
        self.data = pd.read_csv(dir_steering_path)
        self.create_signal()
        self.slider.setMaximum(max(list(self.signal.keys())))
        self.load_signal(0)

    def on_dir_change(self, curr, prev):
        self.current_dir = curr
        self.load_new_dir()

    def change_signal(self, signal_number):
        self.load_signal(signal_number)
        signal = self.signal[signal_number]
        t = signal['date']
        tim = t.strftime("%H:%M:%S.%f")
        signal = "".join([k if signal[k]==True else '' for k in "wsad"])
        self.image_data.setText("Number:{}/{} Time:{} \n Signal:{}".format(signal_number, max(list(self.signal.keys())), tim, signal))

    def delete_frames(self, min_id, max_id=0):
        if max_id == 0:
            max_id = min_id

        frames_to_remove = [self.signal[x] for x in [min_id, max_id]]
        for frame_to_remove in frames_to_remove:
            filename = os.path.join(self._current_dir, frame_to_remove['filenames'])
            if os.path.isfile(filename):
                os.remove(filename)

        self.data = self.data.drop(self.data.index[[min_id, max_id]])
        self.create_signal()
        self.slider.setMaximum(max(list(self.signal.keys())))

        dir_steering_path = os.path.join(self.current_dir,self.steering_file)
        self.data.to_csv(dir_steering_path)
        self.change_signal(self.slider.value())

    def delete_frame(self):
        self.delete_frames(self.slider.value())

    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.video_size)
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.delete_button = QPushButton("Delete frame")
        self.delete_button.clicked.connect(self.delete_frame)

        self.main_layout = QHBoxLayout()
        self.image_layout = QVBoxLayout()
        self.image_layout.addWidget(self.image_label)
        self.image_data = QLabel()
        self.image_layout.addWidget(self.image_data)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setTickInterval(1)
        self.slider.setMaximum(1)
        self.slider.valueChanged.connect(self.change_signal)
        self.image_layout.addWidget(self.slider)
        self.main_layout.addLayout(self.image_layout)
        self.file_list = QListWidget()
        self.file_list.addItems(self.dirlist)
        self.file_list.currentItemChanged.connect(self.on_dir_change)
        self.right_panel = QVBoxLayout()
        self.right_panel.addWidget(self.quit_button)
        self.right_panel.addWidget(self.delete_button)
        self.right_panel.addWidget(self.file_list)
        self.main_layout.addLayout(self.right_panel)
        self.setLayout(self.main_layout)

    def display_video_stream(self):
        signal = self.signal
        image = QImage(signal, signal.shape[1], signal.shape[0], signal.strides[0], QImage.Format_RGB888)
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



