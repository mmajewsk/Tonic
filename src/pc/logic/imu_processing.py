import time
import numpy as np
import pandas as pd
import os

from logic.filtering import KalmanFilter, SimpleCalibration, TiltCorrector


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
	def __init__(
				self,
				conv_acc= 0.01,
				conv_gyr= 70,
				conv_mag=1,
				calib_size=20,
				recalib_size=15,
				dump_dir='',
				dump_imu=False,
				):
		self.log_acc = []
		self.log_gyr = []
		self.log_mag = []
		self.log_all = []
		self.raw_log_acc = []
		self.raw_log_gyr = []
		self.raw_log_mag = []
		self.raw_log_all = []
		#self.logger =
		self.conv_acc = conv_acc
		self.conv_gyr = conv_gyr
		self.conv_mag = conv_mag
		self.units_acc = "cm/s^2"
		self.units_gyr = ''
		self.units_mag = ''
		self.calib_size = calib_size
		self.recalib_size = recalib_size
		self.last_recalib = True
		self.dump_dir = dump_dir
		self.dump_name = 'imu.csv'
		self.dump_path = os.path.join(self.dump_dir, self.dump_name) if self.dump_dir!= None else None
		self.dump_imu = dump_imu

	def log(self, imu):
		self.log_acc.append(imu.acc)
		self.log_gyr.append(imu.gyr)
		self.log_mag.append(imu.mag)
		self.log_all.append(imu.data)

	def log_recalib(self):
		self.log_acc.append(None)
		self.log_all.append(None)

	def raw_log(self, imu):
		self.raw_log_acc.append(imu.acc)
		self.raw_log_gyr.append(imu.gyr)
		self.raw_log_mag.append(imu.mag)
		self.raw_log_all.append(imu.data)


	def _process(self, data:Imu):
		data.acc = self.calibrator_acc.apply(data.acc)
		data.acc = self.calman_filter.update(data.acc)
		data.acc = self.tilt.correct_tilt(data.acc)
		data.acc = data.acc.astype(int)
		data.gyr = self.calibrator_gyr.apply(data.gyr)
		data.acc = data.acc*self.conv_acc
		data.gyr = data.gyr*self.conv_gyr
		data.mag = data.mag*self.conv_mag
		return data

	def _create_calibrators(self):
		self.calibrator_acc = SimpleCalibration(self.log_acc, apply_treshold=False)
		print("Created calibrator for acc:\n{}".format(self.calibrator_acc))
		self.calibrator_gyr = SimpleCalibration(self.log_gyr)
		print("Created calibrator for gyr:\n{}".format(self.calibrator_gyr))
		self.calman_filter = KalmanFilter(self.calibrator_acc.stdev)
		self.tilt = TiltCorrector(self.calibrator_acc.mean,[0,0,-1])
		print("Created tilt corrector\n {}".format(self.tilt))

	def _check_recalib(self):
		if np.all(self.log_gyr[-1]==0.0):
			calibrator = SimpleCalibration(self.log_gyr[-self.recalib_size:])
			recalib_diff = len(self.log_acc)-self.last_recalib
			if np.all(calibrator.mean<self.calibrator_gyr.stdev) and recalib_diff>100:
				self.calibrator_acc.level_out(self.raw_log_acc[-self.recalib_size:])
				self.calman_filter = KalmanFilter(self.calibrator_acc.stdev)
				print("Recalibrated acc:\n{}".format(self.calibrator_acc))
				self.last_recalib=len(self.log_acc)
				self.log_recalib()
		''''
		tmp2 = len(self.log_acc)-600
		if (tmp2)%self.recalib_size==0 and tmp2>0:
			tmp = np.mean(self.log_acc,axis=0)
			tc = TiltCorrector(tmp,[1,0,0])
			print(tc)
		'''

	def imu_from_raw(self, raw_data)->Imu:
		data = Imu(raw_data)
		if len(self.log_acc) > self.calib_size:
			self._check_recalib()
			data = self._process(data)
		elif len(self.log_acc) == self.calib_size:
			self._create_calibrators()
			data = self._process(data)
		self.log(data)
		self.raw_log(ImuTimed(raw_data))
		return data

	def recalibrate(self):
		calib_data = self.log_acc[-self.calib_size:]
		self.calibrator_acc.level_out(calib_data)

	def dump_logs(self):
		if self.dump_path:
			log = np.array(self.raw_log_all)
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
