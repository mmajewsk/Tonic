from logic import Mapper


def calculate_metric(img_a, img_b, transformation):
	metric = 0
	return metric

class Stitcher:
	"""
	Algorith:
	1. Receive two images A and B and initial transformation guess of B
	2. Create overlapping of images
	3. Check the simmilarity metric M_0
	4. Check the change of metric, by moving the B by 1px in 4 dimensions
	5. Choose the lowest result (minimize difference)
	6. Repeat 4-5 until no onger minimizing

	"""

	def __init__(self, img_a, img_b, transformation):
		self.img_a = img_a
		self.img_b = img_b
		self.initial_guess = transformation



	def directional_translation(self, transformation, step_change):
		(x, y) = step_change
		transformation += (x,y)
		return transformation

	def step(self, transformation):
		step_changes = [(1,0),(0,1),(-1,0), (0,-1)]
		get_metric = lambda x : self.directional_translation(transformation,x)
		steps = map(get_metric, step_changes)
		get_change = lambda x: calculate_metric(self.img_a, self.img_b, x)
		changes = map(get_change, steps)
		best_change = min(changes)
		best_transformation = steps[changes.index(best_change)]
		return best_change, best_transformation


	def work(self):
		old_metric = calculate_metric(self.img_a, self.img_a, self.initial_guess)
		converging = True
		transformation = None
		while converging:
			new_metric, transformation = self.step(transformation)
			gradient = old_metric - new_metric
			converging = gradient > 0.
		return transformation
