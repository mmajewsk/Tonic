from logic.action import Action
from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
import cv2
import numpy as np

class Velo(Action):
	def __init__(self):
		pass

	def action(self, **kwargs):
		return self.inverse(kwargs['img'])

def to_inverse_perspective(perspective, img):
	img = cal.undistort(img)
	img[:155, :, :] = 0
	img = perspective.inverse(img)
	cv2.imshow('persp', img)
	return img


def gamma_correction(img, correction):
	img = img/255.0
	img = cv2.pow(img, correction)
	return np.uint8(img*255)

def processing(img):
	proc = img.copy()
	#proc = proc[145:proc.shape[1], roi[0][0] - 5:roi[2][0] + 5, :]
	proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
	#proc = cv2.fastNlMeansDenoising(proc, None, 2, 4, 5)
	#cv2.imshow('denoise', proc)
	#proc = cv2.equalizeHist(proc,)
	#proc = gamma_correction(proc, 0.9)
	#kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
	#proc = cv2.filter2D(proc, -1, kernel)
	#cv2.imshow('equal', proc)
	#proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
	#cv2.imshow('adap', proc)
	#proc = cv2.Canny(proc, 20, 150, apertureSize=3)
	#cv2.imshow('edge', proc)
	return proc

if __name__=='__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3\v1.23"
	perspective = InversePerspective(img_shape=(250,250), desired_shape=(80,160), marigin=0.25)
	import os
	import pandas as pd
	pd.read_csv(os.path.join(dirpath,'vis_v1.csv'))
	images = os.listdir(dirpath)
	images = filter(lambda x: ".jpg" in x, images)
	images = map(lambda x: os.path.join(dirpath, x), images)
	images = list(images)
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
	orb = cv2.ORB_create(nfeatures=5000, scaleFactor=2., )#, edgeThreshold=17, patchSize=64)
	vx_list = []
	vy_list = []
	for i in range(1,len(images)):
		img_path_1 = images[i]
		img_path_0 = images[i-1]
		img_0 = cv2.imread(img_path_0)
		img_1 = cv2.imread(img_path_1)
		if np.equal(img_0,img_1).all():
			continue
		#img_0 = to_inverse_perspective(perspective, img_0)
		#img_1 = to_inverse_perspective(perspective, img_1)
		proc = np.zeros(img_1.shape)
		roi = perspective.destination.astype(np.int)
		processed1 = processing(img_1)
		processed0 = processing(img_0)
		mask1 = perspective.roi_mask
		mask2 = perspective.roi_mask
		#processed0 = cv2.bitwise_and(processed0, processed0,  mask=mask1)
		#processed1 = cv2.bitwise_and(processed1, processed1,  mask=mask2)
		flowUmat = cv2.calcOpticalFlowFarneback(
			processed0,
			processed1,
			None,
			pyr_scale=0.4,
			levels=2,
			winsize=24,
			iterations=2,
			poly_n=8,
			poly_sigma=1.8,
			flags=0)
		flow = flowUmat.copy()
		original = processed1.copy()
		flow2 = flow * 6
		for y in range(0, original.shape[0], 5):
			for x in range(0, original.shape[1], 5):
				flowatxy = flow2[y, x]
				x2 = int(round(x + flowatxy[0]))
				y2 = int(round(y + flowatxy[1]))
				cv2.line(original, (x, y), (x2, y2), (255, 0, 0))
				cv2.circle(original, (x, y), 1, (0, 0, 0), -1)
		cv2.imshow("prew", original)
		scale = 80
		vx = -flow[:,:,0].mean()*scale
		vy = -flow[:,:,1].mean()*scale
		x0 = img_1.shape[1]//2
		y0 = img_1.shape[0]-60
		x1 = int(x0 + vx)
		y1 = int(y0 + vy)
		cv2.line(img_1, (x0,y0), (x1,y1), (255, 0, 0), 6)
		cv2.imshow('velo', img_1)
		cv2.waitKey(20)
	cv2.destroyAllWindows()
