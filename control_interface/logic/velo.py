from logic.action import Action
from logic.calibration import VideoCalibration
from logic.inverse_perspective import InversePerspective
import cv2
import numpy as np

class Velo(Action):
	def __init__(self):
		pass

	def action(self, **kwargs):
		return self.inverse(kwargs['img'])

def to_inverse_perspective(perspective, img):
	img = cal.undistort(img)
	img[:155, :, :] = 0
	img = perspective.inverse(img)
	cv2.imshow('persp', img)
	return img



def cross_iterate(point, cross_size=15):
	#@deprecated
	x,y = point
	points= [
		(x-cross_size,y),
		(x,y-cross_size),
		(x+cross_size,y),
		(x,y+cross_size)
		]
	return points

def get_cross_values(point, img):
	return [img[int(y),int(x)] for (x,y) in cross_iterate(point)]

def is_edge_match(match:cv2.DMatch, train_img, query_img, train_keys, query_keys):
	t_point, q_point = train_keys[match.queryIdx].pt, query_keys[match.trainIdx].pt
	t_cross = get_cross_values(t_point, train_img)
	q_cross = get_cross_values(q_point, query_img)
	black_list = list(map(lambda x:(x<=[10,10,10]).any(),t_cross+q_cross))
	return any(black_list)


def gamma_correction(img, correction):
	img = img/255.0
	img = cv2.pow(img, correction)
	return np.uint8(img*255)

def processing(img):
	proc = img.copy()
	#proc = proc[145:proc.shape[1], roi[0][0] - 5:roi[2][0] + 5, :]
	proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
	proc = cv2.fastNlMeansDenoising(proc, None, 2, 4, 5)
	cv2.imshow('denoise', proc)
	#proc = cv2.equalizeHist(proc,)
	#proc = gamma_correction(proc, 0.9)
	#kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
	#proc = cv2.filter2D(proc, -1, kernel)
	#cv2.imshow('equal', proc)
	#proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
	#cv2.imshow('adap', proc)
	#proc = cv2.Canny(proc, 20, 150, apertureSize=3)
	cv2.imshow('edge', proc)
	return proc

if __name__=='__main__':
	cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
	cal = VideoCalibration(cal_data, (320, 240))
	dirpath = r"C:\repositories\autonomic_car\selfie_car\data_intake3\v1.20"
	marigin = 15
	"""
			(102,153),
		(205,153),
		(320-54, 240-15),
		(0+43,240-17),

			(70,169),
		(227,169),
		(320-28, 240-23),
		(0+12,240-24),
	"""
	perspective = InversePerspective(img_shape=(250,250), desired_shape=(80,160), marigin=0.25)
	import os

	images = os.listdir(dirpath)
	images = filter(lambda x: ".jpg" in x, images)
	images = map(lambda x: os.path.join(dirpath, x), images)
	images = list(images)
	bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
	orb = cv2.ORB_create(nfeatures=5000, scaleFactor=2., )#, edgeThreshold=17, patchSize=64)

	for i in range(1,len(images)):
		img_path_1 = images[i]
		img_path_0 = images[i-1]
		img_0 = cv2.imread(img_path_0)
		img_1 = cv2.imread(img_path_1)

		img_0 = to_inverse_perspective(perspective, img_0)
		img_1 = to_inverse_perspective(perspective, img_1)
		proc = np.zeros(img_1.shape)
		roi = perspective.destination.astype(np.int)
		processed1 = processing(img_1)
		processed0 = processing(img_0)
		#img_0 = img[]
		mask1 = perspective.roi_mask
		mask2 = perspective.roi_mask
		img_0 = processed0
		img_1 = processed1
		kp1, des1 = orb.detectAndCompute(img_0, mask1)
		kp2, des2 = orb.detectAndCompute(img_1, mask2)
		img4 = cv2.drawKeypoints(img_0,  kp1, None, color=(0, 255, 0), flags=0)
		cv2.imshow('keypoints', img4)
		try:
			matches = bf.match(des1, des2)
		except cv2.error as e:
			print(e)
		else:
			matches = sorted(matches, key=lambda x: x.distance)
			# matches = filter(lambda x: is_edge_match(x,img_0, img_1, kp1, kp2), matches)
			matches = list(matches)
			# matches = matches[:10]
			img3 = cv2.drawMatches(img_0, kp1, img_1, kp2, matches, (1200, 600), flags=2)

		finally:
			pass


		cv2.imshow('features', img3)
		cv2.waitKey(20)
	cv2.destroyAllWindows()
