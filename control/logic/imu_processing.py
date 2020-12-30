import time
import numpy as np
import pandas as pd
import os

import warnings

def data_to_array(data):
	return np.reshape(np.array(data),(3,3))

def rp_from_acc(acc_data):
	x,y,z = acc_data[0],acc_data[1],acc_data[2]
	roll = np.arctan2(y, z) * 180 / np.pi
	pitch = np.arctan2(-x, np.sqrt(y *y + z * z)) * 180.0 / np.pi
	return roll, pitch


class Imu:
	def __init__(self, data:np.ndarray):
		self.acc = data[:3]
		self.gyr = data[3:6]
		self.mag = data[6:]

	def _data(self):
		self.list = [self.acc, self.gyr, self.mag]
		return np.array(self.list).reshape((1,9))[0]

	@property
	def data(self):
		return self._data()


class ImuTimed(Imu):
	def __init__(self, data:np.ndarray, t:float=None):
		Imu.__init__(self, data)
		self.time = time.time() if t==None else t

	@property
	def data(self):
		return np.append(Imu._data(self), self.time)


class ImuKeeper:
	def __init__(self, dump_dir='', dump_imu=False):
		self.raw_log_acc = []
		self.raw_log_gyr = []
		self.raw_log_mag = []
		self.raw_log_all = []
		self.dump_dir = dump_dir
		self.dump_name = 'imu.csv'
		self.dump_path = os.path.join(self.dump_dir, self.dump_name) if self.dump_dir != None else None
		self.dump_imu = dump_imu

	def raw_log(self, imu: Imu):
		self.raw_log_acc.append(imu.acc)
		self.raw_log_gyr.append(imu.gyr)
		self.raw_log_mag.append(imu.mag)
		self.raw_log_all.append(imu.data)

	def rotation(self, raw_data) -> Imu:
		self.raw_log(ImuTimed(raw_data))
		data = Imu(raw_data)
		return data

	def dump_logs(self):
		if self.dump_path:
			log = np.array(self.raw_log_all)
			np.savetxt(self.dump_path+'2', log, delimiter='\t')
			data={'acc_x':log[:,0],
				  'acc_y':log[:,1],
				  'acc_z':log[:,2],
				  'gyr_x':log[:,3],
				  'gyr_y':log[:,4],
				  'gyr_z':log[:,5],
				  'mag_x':log[:,6],
				  'mag_y':log[:,7],
				  'mag_z':log[:,8],
				  'time':log[:,9]}
			df = pd.DataFrame(data)
			df.to_csv(self.dump_path)


