import argparse
import shutil
import json
import os

if __name__ == '__main__':
    """
    examplary arguments:
        /home/mwm/repositories/slam_dunk/builds/data/ORBvoc.txt /home/mwm/repositories/os2py_applied/TUM-MINE-wide.yaml /home/mwm/Desktop/datadumps/01-07-19-drive-v1_22/ --start 250 --end 500
    """
    parser = argparse.ArgumentParser(description='Usage: ./orbslam_mono_tum path_to_vocabulary path_to_settings path_to_sequence')
    parser.add_argument('assoc_file', help="A path to voabulary file from orbslam. \n"
                                           "E.g: ORB_SLAM/Vocabulary/ORBvoc.txt")
    parser.add_argument('images_path', help="Path to the folder with images")
    parser.add_argument('images_dump', help="Path to the folder with images")
    args = parser.parse_args()
    with open(args.assoc_file) as f:
        assoc_dict = json.load(f)
    for el in assoc_dict["keyframes"]:
        if isinstance(el, list):
            if not os.path.exists(args.images_dump):
                os.makedirs(args.images_dump)
            nr, ts, filename = el
            shutil.copy2(os.path.join(args.images_path, filename), args.images_dump)
