import os
import cv2

def load_images(path_to_association):
    rgb_filenames = []
    timestamps = []
    with open(os.path.join(path_to_association, 'rgb.txt')) as times_file:
        for i, line in enumerate(times_file):
            if i < 3:
                # why ? i dont know, but its in the xample so do it
                continue
            if len(line) > 0 and not line.startswith('#'):
                t, rgb = line.rstrip().split(' ')[0:2]
                rgb_filenames.append(rgb)
                timestamps.append(float(t))
    return rgb_filenames, timestamps

def read_folder_as_tuples(images_path):
    filenames, timestamps = load_images(images_path)
    return [(cv2.imread(os.path.join(images_path, filename)), float(timestamp)) for filename, timestamp in zip(filenames, timestamps)]
