import pandas as pd
from logic.action import Action
from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.integrate
from logic.filtering import KalmanFilter

class Velo(Action):
	def __init__(self):
		self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		self.orb = cv2.ORB_create(nfeatures=5000, scaleFactor=2., )  # , edgeThreshold=17, patchSize=64)

	def preprocessing(self, img):
		proc = img.copy()
		proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
		return proc

	def flow(self, img1, img2):
		if np.equal(img1,img2).all():
			return None
		processed1 = self.preprocessing(img1)
		processed2 = self.preprocessing(img2)
		flowUmat = cv2.calcOpticalFlowFarneback(
			processed1,
			processed2,
			None,
			pyr_scale=0.4,
			levels=2,
			winsize=24,
			iterations=2,
			poly_n=8,
			poly_sigma=1.8,
			flags=0)
		return flowUmat

	def speed(self, img1, img2):
		flow = self.flow(img1, img2)
		if flow is None:
			return None
		vx = -flow[:, :, 0].mean()
		vy = -flow[:, :, 1].mean()
		return vx, vy

	def grid_flow(self, img, flow):
		for y in range(0, img.shape[0], 5):
			for x in range(0, img.shape[1], 5):
				flowatxy = flow[y, x]
				x2 = int(round(x + flowatxy[0]))
				y2 = int(round(y + flowatxy[1]))
				cv2.line(img, (x, y), (x2, y2), (255, 0, 0))
				cv2.circle(img, (x, y), 1, (0, 0, 0), -1)
		return img

	def action(self, **kwargs):
		return self.inverse(kwargs['img'])


def to_inverse_perspective(perspective, img):
	img = cal.undistort(img)
	img[:155, :, :] = 0
	img = perspective.inverse(img)
	cv2.imshow('persp', img)
	return img

def draw_velo(v, img1):
	vx, vy = v
	x0 = img1.shape[1] // 2
	y0 = img1.shape[0] - 60
	x1 = int(x0 + vx)
	y1 = int(y0 + vy)
	cv2.line(img1, (x0, y0), (x1, y1), (255, 0, 0), 6)
	return img1

def calculate_flow(df, dirpath):
	df['flow_x'] = df['filenames']
	df['flow_y'] = df['filenames']
	img0 = None
	img1 = None
	velo = Velo()
	df.set_value(df.index[0], 'flow_x', 0)
	df.set_value(df.index[0], 'flow_y', 0)
	for i, row in df[1:].iterrows():
		if pd.isnull(row['filenames']) or not isinstance(img0, np.ndarray):
			flow_x=np.nan
			flow_y=np.nan
			if not pd.isnull(row['filenames']):
				img0 = cv2.imread(os.path.join(dirpath, row['filenames']))
		else:
			img1 = cv2.imread(os.path.join(dirpath, row['filenames']))
			v = velo.speed(img0, img1)
			if v is None:
				flow_x = np.nan
				flow_y = np.nan
			else:
				flow_x, flow_y = v
			img0 = img1.copy()
		df.set_value(i,'flow_x',flow_x)
		df.set_value(i,'flow_y', flow_y)
	return df

def calculate_stop(df_orig, window=5):
	df = df_orig.copy()
	df['stop'] = pd.rolling_mean(df['flow_x']*300, window=window)
	df['stop'] = df['stop'].abs()
	threshold = 2.0
	df.loc[df['stop'] <= threshold, 'stop'] = 1.0
	df.loc[df['stop'] > threshold, 'stop'] = 0
	df['stop'] = df['stop'] * 1000
	# df['stop'][df['stop']==1000] = True
	# df['stop'][df['stop']==0] = False
	# df['stop'] = df['stop'].shift(-4)
	return df

if __name__=='__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3\v1.23"
	perspective = InversePerspective(img_shape=(250,250), desired_shape=(80,160), marigin=0.25)
	import os
	df = pd.read_csv(os.path.join(dirpath,'vis_v1.csv'))
	for i, row in df.iterrows():

		cv2.imshow('velo', img1)
		cv2.waitKey(20)
	cv2.destroyAllWindows()
