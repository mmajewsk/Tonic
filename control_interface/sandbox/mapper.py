from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
from logic.velo4 import Velo, calculate_flow, calculate_stop
import pandas as pd
import cv2
from scipy.integrate import cumtrapz
import scipy.signal
import numpy as np
import os
from logic.mapper import Mapper

def retrofit_slice(series, start, stop):
	error = np.arange(stop - start)
	error = error / (1. * error[-1])
	pedestal = series.loc[stop]
	error = error * pedestal
	series.loc[start:stop - 1] -= error
	series.loc[stop:] -= pedestal
	return series, error, pedestal


def fix_drift(df, column):
	for i, rows in df.iterrows():
		value = df[column].loc[i]
		# print(bool(rows['stop']),bool(df['stop'].iloc[i-1]))
		if rows['stop'] == 0 and df['stop'].iloc[i - 1] != 0:
			start = i
		elif rows['stop'] != 0 and df['stop'].iloc[i - 1] == 0:
			# fig = plt.figure()
			# ax1 = fig.add_subplot(111)
			# ax1.plot(df[column].index, df[column], color='green')
			stop = i
			series, error, pedestal = retrofit_slice(df.loc[:, column], start, stop)
			df.loc[:, column] = series
			# ax1.plot(df[column].index, df[column], color='blue')
			# ax1.plot(series[start:stop].index, error, color='red')
			# print(pedestal)
		if rows['stop'] != 0:
			df[column][i:] -= value
			df.set_value(i, column, 0.)
	return df


def lpass(x):
	# spell out the args that were passed to the Matlab function
	N = 10
	Fc = 40
	Fs = 1600
	# provide them to firwin
	h = scipy.signal.firwin(numtaps=N, cutoff=Fc, nyq=Fs / 2)
	return scipy.signal.lfilter(h, 1.0, x)


def integrate(df, target='vel_x', source='gry_x'):
	df.loc[1:, target] = cumtrapz(df[source].values, df['alltimes'].values)
	df.loc[0, target] = df.loc[1, target]
	return df


def calculate_position(df_original, dirpath):
	df = df_original.copy()
	df = calculate_flow(df, dirpath)
	df['flow_x'] = df['flow_x'].fillna(method='ffill')
	df['flow_y'] = df['flow_y'].fillna(method='ffill')
	df = calculate_stop(df)
	df = integrate(df, 'vel_x', 'gyr_x')
	df = integrate(df, 'vel_y', 'gyr_y')
	df = integrate(df, 'vel_z', 'gyr_z')
	df2 = fix_drift(df.copy(), 'vel_y')
	df2 = fix_drift(df2, 'vel_x')
	df2 = fix_drift(df2, 'vel_z')
	df2['vel'] = np.sqrt(df2['vel_y'] ** 2 + df2['vel_x'] ** 2)
	df2 = integrate(df2, 'pos', 'vel')
	df2 = integrate(df2, 'pos_x', 'vel_x')
	df2 = integrate(df2, 'pos_y', 'vel_y')
	return df2

class CarModel:
	def __init__(self):
		self.start_distance = None
		self.start_angle = None
		self.x = 0.0
		self.y = 0.0

	def update(self, distance, angle):
		if self.start_distance == None:
			self.start_distance = distance
			self.previous_distance = self.start_distance
		if self.start_angle == None:
			self.start_angle = angle
		distance -= self.start_distance
		dd = distance - self.previous_distance
		self.previous_distance = distance
		angle -= self.start_angle
		dx = dd*np.sin(np.deg2rad(angle))
		dy = dd*np.cos(np.deg2rad(angle))
		self.x += dx
		self.y += dy



if __name__ == '__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\repositories\autonomic_car\selfie_car\data_intake3\v2.20"
	perspective = InversePerspective(img_shape=(250, 250), desired_shape=(80, 160), marigin=0.25)
	mapper = Mapper(map_size=(1200,1200),scale=1600.0, type='additive')
	df = pd.read_csv(os.path.join(dirpath, 'vis_v1.csv'))
	#df = df[~df['filenames'].isnull()]
	#df = calculate_position(df, dirpath)
	df = pd.read_csv(os.path.join(dirpath, 'pos_v1.csv'))
	car = CarModel()
	for i, row in df.iterrows():
		if pd.isnull(row['filenames']):
			continue
		img = cv2.imread(os.path.join(dirpath, row['filenames']))
		cv2.imshow('velo', img)
		img = cal.undistort(img)
		img[:145, :, :] = 0
		img = perspective.inverse(img)
		cv2.imshow('persp', img)
		angle = row['acc_x']
		angle = angle if row['mag_y']<0 else 180+angle
		car.update(row['pos'], angle)
		position = -car.x, -car.y
		map = mapper.update(img, angle=-angle, position=position)
		cv2.imshow('map', map)
		cv2.waitKey(20)
	cv2.destroyAllWindows()
