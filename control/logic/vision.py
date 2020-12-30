import numpy as np
import cv2
from logic.action import Action
from clients import QTSteeringClient

class StopDetector(Action):
	def __init__(self, classifier_path):
		self.stop_cascade = cv2.CascadeClassifier(classifier_path)
		self.previous_cascade = []

	@staticmethod
	def cascade_obj_equal(a,b):
		for v1, v2 in zip(a,b):
			if v2==0 or abs(1-v1/(1.*v2))>0.1:
				return False
		return True

	def get_cascade_objects(self, img):
		gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY)
		cascade_obj = self.stop_cascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=3,
			minSize=(10, 10),
			flags=0
		)
		if len(self.previous_cascade)==0:
			self.previous_cascade=cascade_obj
			return self.previous_cascade
		if len(cascade_obj)!=0:
			new_cascade = []
			for i, c_new in enumerate(cascade_obj):
				matching_objects = [self.cascade_obj_equal(c_old,c_new) for c_old in self.previous_cascade]
				print(cascade_obj, matching_objects, self.previous_cascade)
				if not any(matching_objects):
					new_cascade.append(c_new)
			self.previous_cascade = new_cascade if len(new_cascade)!=0 else self.previous_cascade
			return self.previous_cascade
		else:
			return cascade_obj

	def action(self, frame, **kwargs):
		cascade_objects = self.get_cascade_objects(frame)
		if cascade_objects is not None:
			for (x_pos, y_pos, width, height) in cascade_objects:
				cv2.rectangle(frame, (x_pos + 5, y_pos + 5), (x_pos + width - 5, y_pos + height - 5), (255, 255, 255), 2)
				v = y_pos + height - 5
				# print(x_pos+5, y_pos+5, x_pos+width-5, y_pos+height-5, width, height)
				cv2.putText(frame, 'STOP', (x_pos, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		return frame, kwargs

class SignalPainter(Action):
	def __init__(self, video_size, draw_border, letters="wsad", radius=5, color_bgr=(255, 0, 0)):
		self.letters = letters
		self.color = color_bgr
		self.thickness = -1
		self.radius = radius
		self.draw_border = draw_border
		self.video_w, self.video_h = video_size
		coord_draw = {
			'a': (self.draw_border, self.video_h//2),
			'd': (self.video_w-self.draw_border, self.video_h // 2),
			'w': (self.video_w//2, self.draw_border),
			's': (self.video_w//2, self.video_h-self.draw_border),
		}
		if letters != 'wsad':
			self.coord_draw = {l: coord_draw[l_wsad] for l_wsad, l in zip('wsad', letters)}
		else:
			self.coord_draw = coord_draw



	def action(self, frame, keys, **kwrgs):
		if keys:
			for	letter in self.letters:
				if keys[letter]:
					x, y = self.coord_draw[letter]
					frame = cv2.circle(frame, (x, y), self.radius, self.color, self.thickness)
		kwrgs['keys'] = keys
		return frame, kwrgs