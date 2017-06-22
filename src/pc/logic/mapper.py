import cv2
import numpy as np


class Mapper:
	def __init__(self, map_size=(800,800), scale=1.0):
		self.map_size = map_size
		self._map = np.zeros((self.map_size[0], self.map_size[1], 3), np.uint8)
		self.start_point = None
		self.conversion_value = scale
		self.map_center = map_size[0]/2, map_size[1]/2

	def convert_measure(self, x):
		return x*self.conversion_value

	def convert_position(self, position):
		p_x, p_y = position
		p_x, p_y = map(lambda x : self.convert_measure(x), (p_x, p_y))
		return p_x, p_y

	def relative_position(self, position):
		p_x, p_y = self.convert_position(position)
		p_x, p_y = p_x - self.start_point[0], p_y - self.start_point[1]
		return p_x, p_y

	def update(self, frame, angle=0, position=(0,0)):
		if self.start_point is None:
			self.start_point = position
		else:
			relative_position = self.relative_position(position)
		print(angle)
		rot = cv2.getRotationMatrix2D((120,120), angle, scale=1)
		frame = cv2.cvtColor(frame.astype(np.uint8),cv2.COLOR_RGB2GRAY)
		dst = cv2.warpAffine(src=frame, M=rot, dsize=frame.shape)
		self._map = dst
		return self._map