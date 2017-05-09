import cv2
import cv2.ml
import numpy as np
from sklearn.cross_validation import train_test_split
import pandas as pd
from PIL import Image

DATA_DIR = 'C:/users/Wojtek/Dropbox/data_intake/'


def load_data(train_folder):
    image_array = np.zeros((1, 19200))
    df = pd.read_csv(train_folder + '/steering_filtered.csv')
    train_labels = df.loc[df['filtered'] == True][['w', 's', 'a', 'd']].as_matrix()
    train_images = df.loc[df['filtered'] == True][['filenames']].as_matrix()
    for train_image in train_images:
        image_path = train_folder + '/' + train_image
#         print(image_path)
        pic = Image.open(image_path[0])
        pix = np.array(pic)
        small = cv2.resize(pix, (0, 0), fx=0.5, fy=0.5)
#         print(small[:,:,1].flatten().shape)
        image_array = np.vstack((image_array, small[:, :, 1].flatten()))
    train = image_array[1:, :]
    return train, train_labels


data_description_filename = 'data_description.csv'
steering_filename = 'steering_filtered.csv'

dataset_file = open(DATA_DIR + data_description_filename, 'r')
datasets = dataset_file.readlines()

datasets_path = [DATA_DIR + s.rstrip() for s in datasets]

train_folders, test_folders = train_test_split(datasets_path, test_size=0.25, random_state=42)

# load training data
train = np.zeros((1, 19200))
train_labels = np.zeros((1, 4), 'float')

for train_folder in train_folders[:2]:
    print(train_folder)
    train_temp, train_labels_temp = load_data(train_folder)
    train = np.vstack((train, train_temp))
    train_labels = np.vstack((train_labels, train_labels_temp))

train = train[1:, :]
train_labels = train_labels[1:, :]

print(train.shape)
print(train_labels.shape)

layer_sizes = np.int32([19200, 32, 4])
model = cv2.ml.ANN_MLP_create()
model.setLayerSizes(layer_sizes)
model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)
criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 500, 0.0001)
criteria2 = (cv2.TERM_CRITERIA_COUNT, 100, 0.001)
params = dict(term_crit = criteria,
               train_method = cv2.ml.ANN_MLP_BACKPROP,
               bp_dw_scale = 0.001,
               bp_moment_scale = 0.0 )


num_iter = model.train(np.float32(train), cv2.ml.ROW_SAMPLE, np.float32(np.float32(train_labels)*2 - 1))

test = np.zeros((1, 19200))
test_labels  = np.zeros((1, 4), 'float')

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

# clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
