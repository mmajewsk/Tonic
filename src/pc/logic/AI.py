from abc import ABCMeta, abstractmethod
import cv2
from clients.steering_client import SetSteering
import numpy as np
from logic.action import Action

class AI(metaclass=ABCMeta):
	def __init__(self, model):
		self.model = model

	@abstractmethod
	def prepare_input(self, img):
		pass

	@abstractmethod
	def translate(self, prediction):
		pass

	def get_action(self, img):
		input = self.prepare_input(img)
		prediction = self.model.predict(input)
		translated_prediction = self.translate(prediction)
		return translated_prediction


class OpencvAI(AI, Action):
	key_sequence = ['w', 's', 'a', 'd']

	def __init__(self, model_path, override_steering=False):
		self.override = override_steering
		model = cv2.ml.ANN_MLP_load(model_path)
		AI.__init__(self, model)

	def prepare_input(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
		img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
		input = img[:, :, 1].flatten()
		return input

	def translate(self, prediction):
		ret, resp = prediction
		resp = resp[0]
		resp[resp>0] = 1
		resp[resp<0] = 0
		return np.bool(resp)

	def action(self, img, keys, **kwargs):
		if True in keys.values():
			return img, keys
		else:
			new_keys = self.get_action(img)
			response = {}
			for letter, value in self.key_sequence, new_keys:
				response[SetSteering.to_letters_dict[letter]] = value
			return img, response



