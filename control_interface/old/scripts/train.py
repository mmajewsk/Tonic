import cv2
import cv2.ml
import numpy as np
from sklearn import cross_validation
import pandas as pd
import os

DATA_DIR = r'C:\Users\hawker\Dropbox\Public\data_intake'
# DATA_DIR = 'C:/users/Wojtek/Dropbox/data_intake/'


def load_data(train_folder):
	image_array = []
	df = pd.read_csv(os.path.join(train_folder, 'steering_filtered.csv'))
	df = df[df['filtered'] == True]
	train_labels = df[['w', 's', 'a', 'd']].as_matrix()
	train_images = df['filenames'].as_matrix()
	for train_image in train_images:
		image_path = os.path.join(train_folder,train_image)
		pic = cv2.imread(image_path)
		small = cv2.resize(pic, (0, 0), fx=0.5, fy=0.5)
		#print(small[:,:,1].flatten().shape)
		image_array.append(small[:, :, 1].flatten())
	train = np.array(image_array)
	#train = image_array[1:, :]
	return train, train_labels

def get_model(training_data_size):
	layer_sizes = np.int32([training_data_size, 32, 4])
	model = cv2.ml.ANN_MLP_create()
	model.setLayerSizes(layer_sizes)
	model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)
	criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001)
	criteria2 = (cv2.TERM_CRITERIA_COUNT, 100, 0.001)
	params = dict(term_crit=criteria,
				  train_method=cv2.ml.ANN_MLP_BACKPROP,
				  bp_dw_scale=0.001,
				  bp_moment_scale=0.0)
	return model

def get_data(train_folders):
	data = [load_data(train_folder) for train_folder in train_folders[:2]]
	train, train_labels = map(list, zip(*data))
	train, train_labels = map(np.array, (train, train_labels))
	train, train_labels = map(np.vstack, (train, train_labels))
	return train, train_labels

def read_folders():
	data_description_filename = 'data_description.csv'
	steering_filename = 'steering_filtered.csv'
	with open(os.path.join(DATA_DIR, data_description_filename), 'r') as dataset_file:
		datasets = dataset_file.read()
	datasets_path = [os.path.join(DATA_DIR, intake_name) for intake_name in datasets.split("\n")]
	train_folders, test_folders = cross_validation.train_test_split(datasets_path, test_size=0.25, random_state=42)
	return train_folders, test_folders

def test_model(model, test_folders):
	for test_folder in test_folders:
		print(test_folder)
		test, test_labels = load_data(test_folder)
		ret, resp = model.predict(np.float32(test))
		df1 = pd.DataFrame(resp)
		df1[df1 < 0] = 0
		df1[df1 > 0] = 1
		df2 = pd.DataFrame(test_labels)
		print(((df1 - df2) ** 2).mean() ** .5)
		df = pd.read_csv((test_folder + "/steering_v1.csv"))
		df.loc[101:250, ['w', 's', 'a', 'd']] = df1.astype(bool).values
		df.to_csv(test_folder + "/steering_nn.csv")


def main():
	training_data_size = 19200
	train_folders, test_folders = read_folders()
	train, train_labels = get_data(train_folders)
	print(train.shape)
	print(train_labels.shape)

	model = get_model(training_data_size)
	num_iter = model.train(np.float32(train), cv2.ml.ROW_SAMPLE, np.float32(np.float32(train_labels)*2 - 1))
	test = np.zeros((1, training_data_size))
	test_labels  = np.zeros((1, 4), 'float')
	test_model(model, test_folders)

if __name__ == "__main__":
	main()
