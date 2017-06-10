import numpy as np
from quaternions import Quaternion as Q

class KalmanFilter:
	def __init__(self, error_measurement, starting_point=None):
		self.shape = error_measurement.shape
		self.error_estimation = error_measurement
		self.error_measurement = error_measurement
		self.previous_estimation = np.zeros(self.shape) if starting_point is None else starting_point

	def update(self, measurement):
		kalman_gain = (self.error_estimation)/(self.error_estimation+self.error_measurement)
		estimate = self.previous_estimation + kalman_gain*(measurement-self.previous_estimation)
		self.error_estimation = (1-kalman_gain)*self.error_estimation
		self.previous_estimation = estimate
		return estimate


class SimpleCalibration:
	def __init__(self, calib_data, mean=None, common_axes=False, apply_treshold=True, normalize=False):
		data = np.array(calib_data)
		self.mean = np.mean(data,axis=0)
		self.pedestal = self.mean if mean==None else mean
		self.normalize = normalize
		if common_axes:
			self.mean = np.mean(self.mean)
		self.norm = np.linalg.norm(self.mean)
		self.stdev = np.std(data,axis=0)
		self.apply_threshold = apply_treshold
		self.threshold = 3*self.stdev
		self.threshold = self.threshold.astype(int)


	def apply(self, raw):
		data = raw - self.pedestal
		if self.apply_threshold:
			data = (data/self.threshold).astype(int) #unitize
			data = data*self.threshold
		if self.normalize:
			data = data/self.norm
		return data

	def level_out(self, calib_data):
		data = np.array(calib_data)
		print(self.mean)
		self.mean = np.mean(data, axis=0)
		self.pedestal = self.mean

	def __str__(self):
		return "Mean:{} \n STD:{}\n norm:{}".format(self.mean, self.stdev, self.norm)

class TiltCorrector:
	def __init__(self, base_acc, desired_acc):
		v1 = base_acc
		v2 = np.array(desired_acc)
		v1 = v1 / np.linalg.norm(v1)
		k = np.cross(v1, v2)
		w = 1.0 + v1.dot(v2)
		q = Q(w, *k)
		q = q.unit()
		#self.q2 = Q(0.638554171917, 0.0, 0.730193472549, -0.243035104817)
		self.q = q

	def correct_tilt(self, vector):
		norm = np.linalg.norm(vector)
		vector = vector / norm
		q1 = Q(0, *vector)
		r = self.q*q1*self.q.conjugate()
		#r = self.q2*r*self.q2.conjugate()
		return (np.array([r.x, r.y, r.z])*norm).astype(int)

	def __str__(self):
		return "Tilt correction quaternion:\n{}".format(self.q)