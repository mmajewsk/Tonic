import json
import cv2
import os
import orbslam2
import argparse
from basic_usage import load_images, read_folder_as_tuples


if __name__ == '__main__':
    """
    examplary arguments:
        /home/mwm/repositories/slam_dunk/builds/data/ORBvoc.txt /home/mwm/repositories/os2py_applied/TUM-MINE-wide.yaml /home/mwm/Desktop/datadumps/01-07-19-drive-v1_22/ --start 250 --end 500
    """
    parser = argparse.ArgumentParser(
        description='Usage: ./orbslam_mono_tum path_to_vocabulary path_to_settings path_to_sequence')
    parser.add_argument('vocab_path', help="A path to voabulary file from orbslam. \n"
                                           "E.g: ORB_SLAM/Vocabulary/ORBvoc.txt")
    parser.add_argument('settings_path', help="A path to configurational file, E.g: TUM.yaml")
    parser.add_argument('images_path', help="Path to the folder with images")
    parser.add_argument('--save_map', type=str, default=None, help="a path name to save map to")
    parser.add_argument('--load_map', type=str, default=None, help="path of the map to be loaded")
    parser.add_argument('--start', type=int, default=0, help="Number of starting frame")
    parser.add_argument('--end', type=int, default=None, help="Number of ending frame")
    args = parser.parse_args()
    vocab_path = args.vocab_path
    settings_path = args.settings_path
    filenames, timestamps = load_images(args.images_path)
    data_tuple = read_folder_as_tuples(args.images_path)
    slam = orbslam2.System(vocab_path, settings_path, orbslam2.Sensor.MONOCULAR)
    slam.set_use_viewer(True)
    slam.initialize()
    slam.osmap_init()
    slam.activate_localisation_only()
    first_datapoint = data_tuple[args.start]
    slam.process_image_mono(first_datapoint[0], first_datapoint[1])
    new_ids = []
    if args.end is None:
        end = len(data_tuple) - 1
    elif abs(args.start - args.end) < 10:
        print("WARGNING!!! the number of usable frames is less than 10!")
    else:
        end = args.end
    if args.load_map is not None:
        slam.map_load(args.load_map + "/initial_tests.yaml", False, False)
        old_timestamps = [kf['mTimeStamp'] for kf in slam.get_keyframe_list()]
        new_ids = [kf['mnId'] for kf in slam.get_keyframe_list()]
    for i, (im, ts) in enumerate(data_tuple[args.start + 1:end]):
        slam.process_image_mono(im, ts)
        print(slam.get_current_pose())

