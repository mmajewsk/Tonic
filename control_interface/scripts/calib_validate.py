import time
import numpy as np
import cv2
import argparse
import os
import sys
sys.path.append('/home/mwm/repositories/Tonic/src/pc/')
from clients import video_client
import multiprocessing

class ServerSource:
	def __init__(self):
		self.tasks = multiprocessing.JoinableQueue()
		self.results = multiprocessing.Queue()
		self.thread_video = video_client.MultiVideoClient(self.tasks, self.results, server_adress=('10.12.10.71', 2201))

	def connect(self):
		self.thread_video.start()

	def get_data(self):
		self.tasks.put(True)
		img=None
		while not self.results.empty():
			img, t = self.results.get()
			#print(img.shape)
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		return img

	@property
	def range(self):
		return range(1000)

class DirectorySource:
	def __init__(self, source_path):
		self.source_path = source_path
		self.pic_i = 0

	def connect(self):
		pics = os.listdir(self.source_path)
		pics = filter(lambda x: ".jpg" in x, pics)
		self.pics = list(pics)

	@property
	def range(self):
		while self.pic_i < len(self.pics):
			yield self.pics[self.pic_i][:-4]
			self.pic_i += 1

	def get_data(self):
		picname = self.pics[self.pic_i]
		picpath = os.path.join(self.source_path, picname)
		img = cv2.imread(picpath)
		return img


def calib(output_folder, live=False, source_folder=None):
	# termination criteria
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

	# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
	objp = np.zeros((6 * 7, 3), np.float32)
	objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)

	# Arrays to store object points and image points from all the images.
	objpoints = []  # 3d point in real world space
	imgpoints = []  # 2d points in image plane.


	valid_images = []

	img = np.zeros((10, 10, 3))
	if live:
		data_source = ServerSource()
	else:
		data_source = DirectorySource(source_path=source_folder)
	data_source.connect()
	for fname in data_source.range:
		img = data_source.get_data()
		if img is None:
			time.sleep(0.3)
			print("no response")
			continue
		if img.shape[0] > 20:
			# Find the chess board corners

			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)

			# If found, add object points, image points (after refining them)
			if ret == True:
				valid = img.copy()
				objpoints.append(objp)
				corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
				imgpoints.append(corners2)
				# Draw and display the corners
				img = cv2.drawChessboardCorners(img, (7, 6), corners2, ret)
				savepath = os.path.join(output_folder,'valid_calib', os.path.basename("{}.jpg".format(fname)))
				print('saved to {}'.format(savepath))
				cv2.imwrite(savepath, valid)
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(img, "Proper frames:{}".format(len(objpoints)), (0, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
		cv2.imshow('img', img)
		cv2.waitKey(1)

	cv2.destroyAllWindows()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('-l', dest='live', action='store_true',
						help='use connection to video server')
	parser.add_argument('folder', metavar='folder', type=str, nargs=argparse.REMAINDER, default=None,
						help='folder to look for calib')
	args = parser.parse_args()
	if len(args.folder)==1:
		calib(args.folder[0], args.live)
	elif len(args.folder)==2:
		calib(args.folder[0], args.live, args.folder[1])