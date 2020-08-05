from abc import ABCMeta, abstractmethod

class Action(metaclass=ABCMeta):

	@abstractmethod
	def action(self, **kwargs):
		pass