from abc import ABCMeta, abstractmethod
import cv2
from clients.steering_client import SteeringClient
import numpy as np
from logic.action import Action


class AI(metaclass=ABCMeta):
	def __init__(self, model):
		self.model = model

	@abstractmethod
	def prepare_input(self, img: np.array) -> np.array:
		"""
		:param img: an opencv image
		:returns: an input for self.model.predict
		"""
		pass

	@abstractmethod
	def translate(self, prediction: np.array) -> np.array:
		"""
		:param prediction: numpy array, result of self.modelpredict
		:return: numpy bool array
		"""
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
		input = img[:, :].flatten()
		input = np.float32(np.reshape(input, newshape=(1, 19200)))
		return input

	def translate(self, prediction):
		ret, resp = prediction
		resp = resp[0]
		resp[resp > 0] = 1
		resp[resp < 0] = 0
		return resp.astype(bool)

	def action(self, frame, keys, **kwargs):
		if keys[17]:
			kwargs['keys'] = keys
			return frame, kwargs
		else:
			new_keys = self.get_action(frame)
			# print(new_keys)
			response = {}
			for letter, value in zip(self.key_sequence, new_keys):
				response[SteeringClient.to_numbers_dict[letter]] = value
			response[17] = False
			kwargs['keys'] = response
			return frame, kwargs
