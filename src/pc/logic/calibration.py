import cv2
from logic.action import Action
import json
import numpy as np

class VideoCalibration(Action):
	def __init__(self, calibration_data, image_shape):
		"""
		Adds calibration_data values as members
		(ret, mtx, dist, rvecs, tvecs)
		:param calibration_data:
		"""
		if isinstance(calibration_data, str):
			calibration_data = json.load(open(calibration_data, 'r'))
		w, h = image_shape
		self.mtx = np.array(calibration_data['mtx'])
		self.dist = np.array(calibration_data['dist'])
		self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))


	def undistort(self, img):
		img = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
		x, y, w, h = self.roi
		img = img[y:y + h, x:x + w]
		return img

	def action(self, **kwargs):
		return self.undistort(kwargs['img'])

if __name__=='__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320,240))
	dirpath = r'C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3\v1.20'
	import os
	images = os.listdir(dirpath)
	images = filter(lambda x: ".jpg" in x, images)
	images = map(lambda x: os.path.join(dirpath,x), images)
	for img_path in images:
		img = cv2.imread(img_path)
		#img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
		img = cal.undistort(img)
		cv2.imshow('img', img)
		cv2.waitKey(20)

	cv2.destroyAllWindows()

