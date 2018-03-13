import cv2
import numpy as np
from scipy.integrate import cumtrapz
from logic.velo4 import calculate_flow, calculate_stop

def retrofit_slice(series, start, stop):
	error = np.arange(stop - start)
	error = error / (1. * error[-1])
	pedestal = series.loc[stop]
	error = error * pedestal
	series.loc[start:stop - 1] -= error
	series.loc[stop:] -= pedestal
	return series, error, pedestal


def integrate(df, target='vel_x', source='gyr_x'):
	cumtrapz_result = cumtrapz(df[source].values, df['alltimes'].values)
	#print(df.loc[1:, target].shape,cumtrapz_result.shape)
	df.loc[1:, target] = cumtrapz_result
	df.loc[0, target] = df.loc[1, target]
	return df

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
		self.on_screen_position = None
		self.on_map_roi = None

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

	@property
	def blanc(self):
		return np.zeros(self.map_shape, np.uint8)

	def get_base(self):
		if self.base is None:
			self.base = np.zeros(self.map_shape, np.uint8)
		if self.map_type == 'show_only':
			return self.blanc
		elif self.map_type == 'additive':
			return self.base

	@property
	def map(self):
		return self._map

	def rotate_image(self, frame, angle):
		center_of_rotation = frame.shape[0] / 2, frame.shape[1] / 2
		rot = cv2.getRotationMatrix2D(center_of_rotation, angle, scale=1)
		frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2GRAY)
		dst = cv2.warpAffine(frame, rot, frame.shape[:2])
		return dst

	@staticmethod
	def get_image_overlap_masks(img1, img2):
		ret, white_on_1 = cv2.threshold(img1, 1, 255, cv2.THRESH_BINARY)
		black_on_1 = ~white_on_1
		ret, white_on_2 = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)
		common_mask = cv2.bitwise_and(white_on_1, white_on_2)
		only_2_mask = cv2.bitwise_and(black_on_1, ~common_mask)
		only_1_mask = cv2.bitwise_and(white_on_1, ~common_mask)
		return only_1_mask, common_mask, only_2_mask

	@staticmethod
	def get_image_overlap_areas(img1, img2):
		new_image_mask, common_mask, base_mask = Mapper.get_image_overlap_masks(img1, img2)
		img2_only = cv2.bitwise_or(img2, img2, mask=base_mask)
		img1_only = cv2.bitwise_or(img1, img1, mask=new_image_mask)
		common_2 = cv2.bitwise_or(img2, img2, mask=common_mask)
		common_1 = cv2.bitwise_or(img1, img1, mask=common_mask)
		return img1_only, common_1, common_2, img2_only

	@staticmethod
	def merge_images(new_img, base):
		base_orig = base.copy()
		only_new_img, common_1, common_2, only_base_img = Mapper.get_image_overlap_areas(new_img, base_orig)
		common_img = cv2.addWeighted(common_2, 0.5, common_1, 0.5, 0.)
		#cv2.imshow('comon_img', common_img)
		new_map = cv2.add(only_base_img, only_new_img)#paste whats dark in present, and white in past
		new_map = cv2.add(new_map, common_img)
		return new_map

	@staticmethod
	def paste_on_base(blanc, new_img, on_map_roi):
		x1, x2, y1, y2 = on_map_roi
		blanc[x1:x2, y1:y2] = new_img
		return blanc


	def update(self, frame, angle=0, position=(0,0)):
		if self.offset is None:
			self.set_offset(position)
		self.on_screen_position = self.on_map_position(position)
		base = self.get_base()
		dst = self.rotate_image(frame, angle)
		self._last_dst = dst.copy()
		self.on_map_roi = self.map_position_to_roi(self.on_screen_position,  dst.shape)
		self.new_on_canvas = self.paste_on_base(self.blanc, dst, self.on_map_roi)
		self._map = self.merge_images(base, self.new_on_canvas)
		self.base = self._map.copy()