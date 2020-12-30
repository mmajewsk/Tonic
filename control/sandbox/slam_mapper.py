from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
import pandas as pd
import os
import cv2
import numpy as np
import quaternion
from logic.mapper import Mapper, calculate_position

def row_to_quaternion(row):
	return np.quaternion(row.q4,row.q1,row.q2,row.q3)

if __name__ == '__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\repositories\autonomic_car\selfie_car\data_intake4\v1.011"
	perspective = InversePerspective(img_shape=(250, 250), desired_shape=(80, 160), marigin=0.25)
	mapper = Mapper(map_size=(1200,1200),scale=300.0, type='additive')
	df = pd.read_csv(os.path.join(dirpath, 'vis_v1.csv'))
	df = df[~df['filenames'].isnull()]
	columns = ['time','x','y','z','q1','q2','q3','q4']
	slam_df = pd.read_csv(os.path.join(dirpath,'slam_trajectory.csv'), sep=' ', names=columns)
#	imu_df = calculate_position(df, dirpath)
	for i, row in slam_df.iterrows():
		#if pd.isnull(row['filenames']):
		#	continue
		slamstamp = float(row['time'])
		diff = df['time'] - slamstamp
		closest_args = diff.abs().argsort()
		closest_name = df.iloc[closest_args.values[0], :]['filenames']
		img = cv2.imread(os.path.join(dirpath, closest_name))
		cv2.imshow('velo', img)
		img = cal.undistort(img)
		img[:145, :, :] = 0
		img = perspective.inverse(img)
		cv2.imshow('persp', img)
		#angle = row['acc_x']
		#angle = angle if row['mag_y']<0 else 180+angle
		quat = row_to_quaternion(row)
		euler = quaternion.as_euler_angles(quat)
		angle = np.rad2deg(euler)[1]
		print(angle)
		position = row['x'],row['z']
		shape =  img.shape
		scaled_image = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
		mapper.update(scaled_image, angle=180+90+angle, position=position)
		map = mapper.map
		cv2.imshow('rotated', mapper._last_dst)
		cv2.imshow('map', map)
		cv2.waitKey(0)
	cv2.destroyAllWindows()
"""
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
"""
