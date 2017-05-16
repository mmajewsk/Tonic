import numpy as np
import cv2
from logic.action import Action
from clients import SteeringClient

class StopDetector(Action):
	def __init__(self, classifier_path):
		self.stop_cascade = cv2.CascadeClassifier(classifier_path)

	def action(self, frame, **kwargs):
		gray = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2GRAY)
		v = 0
		threshold = 150
		cascade_obj = self.stop_cascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=5,
			minSize=(20, 20),
			flags=0
		)
		for (x_pos, y_pos, width, height) in cascade_obj:
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
		for	letter in self.letters:
			print
			if keys[letter]:
				x, y = self.coord_draw[letter]
				frame = cv2.circle(frame, (x, y), self.radius, self.color, self.thickness)
		kwrgs['keys'] = keys
		return frame, kwrgs