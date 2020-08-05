from logic.action import Action
from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
import cv2
import numpy as np
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

if __name__=='__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3\v1.23"
	perspective = InversePerspective(img_shape=(250,250), desired_shape=(80,160), marigin=0.25)
	import os
	import pandas as pd
	df = pd.read_csv(os.path.join(dirpath,'vis_v1.csv'))
	velo = Velo()
	img0 = None
	img1 = None
	data = {'x':[], 'y':[]}
	plt.ion()
	prev_result_trapz_y = 0
	prev_result_trapz_x = 0
	raw_video = []
	raw_imu = []
	imu = []
	first = 0
	df = df[~df['filenames'].isnull()]
	filter=None
	stop = True
	stopsx = []
	stopsy = []
	just_stopped = False
	pedestal = 0.0
	for i,row in df[2:].iterrows():
		if not isinstance(img0, np.ndarray):
			img0 = cv2.imread(os.path.join(dirpath, row['filenames']))
			continue
		img1 = cv2.imread(os.path.join(dirpath, row['filenames']))
		original = img1.copy()
		if np.equal(img0, img1).all():
			#raw_imu.append(raw_imu[-1])
			raw_video.append(raw_video[-1])
			imu.append(imu[-1])
			continue
		else:
			vx, vy = velo.speed(img0, img1)
			vx, vy = map(lambda x: x * 100, (vx, vy))
		if first == 0:
			first=i-1
		img0 = original
		dx = df['alltimes'][i - 2:i].values
		if dx[0]==dx[1]:
			result_trapz_y = prev_result_trapz_y
			result_trapz_x = prev_result_trapz_x
		else:
			_dx = dx[1]-dx[0]
			#_dx = 3.0
			result_trapz_y = scipy.integrate.trapz(df['gry_y'][i - 2:i], dx=_dx) + prev_result_trapz_y
			result_trapz_y = result_trapz_y
			#result_trapz_y = df['gry_y'].values[i-1]*_dx + prev_result_trapz_y
			result_trapz_x = scipy.integrate.trapz(df['gry_x'][i - 2:i], dx=_dx)
			prev_result_trapz_y = result_trapz_y

			prev_result_trapz_x = result_trapz_x
		pita = lambda x,y : np.sqrt(x**2+y**2)
		#raw_imu.append(row['gry_y'])
		y = df['alltimes'][first:i]
		if np.abs(np.array(raw_video[-3:])).mean() < 2.0:
			if stop == False:
				just_stopped = True
			else:
				just_stopped = False
			stop = True
			stopsx.append(vx)
			stopsy.append(y[-2:].values[-1])
		else:
			stop = False
		if just_stopped and len(stopsy)>2:
			prev_stop = stopsy[-2]
			last_stop_i = np.where(df['alltimes'].values == prev_stop)[0][0]
			drive_length = i - last_stop_i
			error = np.arange(drive_length)
			error = error/(1.*error[-1])
			pedestal = pedestal + result_trapz_y
			error = error*pedestal
			print("pedestal {} imulen {} , last_stop_i {}, drive_length {} i {}".format(pedestal, len(imu), last_stop_i, drive_length, i))
			for x in range(drive_length):
				imu[last_stop_i+x-first-1] = imu[last_stop_i+x-first-1] - error[x]
			plt.figure().canvas.draw()
		raw_video.append(vx)
		imu.append(result_trapz_y)
		img1 = draw_velo((vx,vy),img1)
		cv2.putText(img1, "{}".format(round(vx, 3)), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
		cv2.imshow('velo', img1)
		plt.plot(y, imu, color='blue')
		#plt.plot(y, raw_imu, color='red')
		plt.plot(y, raw_video, color='green')
		if stopsx:
			plt.plot(stopsy, stopsx, 'bo', color='red')
		#print('values {} integrated into {} over dx {}'.format(row['gry_y'],result_trapz,dx[1]-dx[0]))
		plt.pause(0.05)
		cv2.waitKey(20)
	cv2.destroyAllWindows()
