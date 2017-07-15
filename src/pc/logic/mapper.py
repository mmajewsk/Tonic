import cv2
import numpy as np


class Mapper:
	def __init__(self, map_size=(800,800, 3), scale=1.0, type='show_only'):
		assert type in ['show_only','additive']
		self.map_type = type
		self.map_size = map_size[:2]
		self.map_shape = map_size
		self._map = np.zeros((self.map_size[0], self.map_size[1], 3), np.uint8)
		self.distance_conversion_value = scale
		self.map_start_point = map_size[0]/2, map_size[1]/2
		self.image_center = 0.5, 1.0 #expresses i.e. 0.5* width, 1*heighth
		self.offset = None
		self.base = None

	def convert_measure(self, x):
		return x*self.distance_conversion_value

	def convert_position(self, position):
		p_x, p_y = position
		p_x, p_y = map(lambda x : self.convert_measure(x), (p_x, p_y))
		return p_x, p_y

	def set_offset(self, position):
		self.offset = self.convert_position(position)

	def on_map_position(self, position):
		p_x, p_y = self.convert_position(position)
		p_x, p_y = p_x - self.offset[0], p_y - self.offset[1]
		p_x, p_y = p_x + self.map_start_point[0], p_y + self.map_start_point[1]
		return p_x, p_y

	def map_position_to_roi(self, position, shape):
		p_x, p_y = position
		x1, x2 = p_x - shape[0]*self.image_center[0], p_x + shape[0]*self.image_center[0]
		y1, y2 = p_y-shape[1],p_y#@TODO fix it to be set up wit self.image_center
		x1, x2, y1, y2 = map(int, (x1,x2,y1,y2))
		return x1,x2,y1,y2

	def get_base(self):
		if self.base is None:
			self.base = np.zeros(self.map_shape, np.uint8)
		if self.map_type == 'show_only':
			return np.zeros(self.map_shape, np.uint8)
		elif self.map_type == 'additive':
			return self.base

	def update(self, frame, angle=0, position=(0,0)):
		if self.offset is None:
			self.set_offset(position)
		on_screen_position = self.on_map_position(position)
		base = self.get_base()
		rot = cv2.getRotationMatrix2D((120,120), angle, scale=1)
		frame = cv2.cvtColor(frame.astype(np.uint8),cv2.COLOR_RGB2GRAY)
		dst = cv2.warpAffine(frame, rot, frame.shape[:2])
		x1, x2, y1, y2 = self.map_position_to_roi(on_screen_position,  dst.shape)
		base_orig = base.copy()
		base[x1:x2, y1:y2] = dst
		ret, th1 = cv2.threshold(base, 1, 255, cv2.THRESH_BINARY)
		alpha = np.zeros(base.shape,np.float)
		alpha = th1.astype(float)/255.0
		base = (alpha* base).astype(np.uint8)
		base_orig = ((1.0 - alpha)* base_orig).astype(np.uint8)
		base = cv2.add(base, base_orig)
		self._map = base
		self.base = base
		return self._map