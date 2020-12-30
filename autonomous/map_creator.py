import json
import time
import cv2
import os
import orbslam2
import argparse
from pathlib import Path


def load_images(path_to_association):
    rgb_filenames = []
    timestamps = []
    with open(os.path.join(path_to_association, "rgb.txt")) as times_file:
        for i, line in enumerate(times_file):
            if i < 3:
                # why ? i dont know, but its in the xample so do it
                continue
            if len(line) > 0 and not line.startswith("#"):
                t, rgb = line.rstrip().split(" ")[0:2]
                rgb_filenames.append(rgb)
                timestamps.append(float(t))
    return rgb_filenames, timestamps


def read_folder_as_tuples(images_path):
    filenames, timestamps = load_images(images_path)
    return [
        (cv2.imread(os.path.join(images_path, filename)), float(timestamp))
        for filename, timestamp in zip(filenames, timestamps)
    ]


class MapDump:
    def __init__(self, dir_path, dump_name):
        self.dir_path = dir_path
        self.dump_name = dump_name
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)

    def save_osmap(self, slam):
        slam.map_save(str(self.dir_path / self.dump_name), False)

    def save_assoc(self, assoc_dict):
        # @TODO this line below shows how the path should be corrected
        # brought an issue here https://github.com/AlejandroSilvestri/osmap/issues/15
        # with open(str(self.dir_path/'assoc.json'), 'w') as f:
        with open(str("assoc.json"), "w") as f:
            josnstring = json.dumps(assoc_dict)
            f.write(josnstring)


if __name__ == "__main__":
    """
    examplary arguments:
        /home/mwm/repositories/slam_dunk/builds/data/ORBvoc.txt /home/mwm/repositories/os2py_applied/TUM-MINE-wide.yaml /home/mwm/Desktop/datadumps/01-07-19-drive-v1_22/ --start 250 --end 500
    """
    parser = argparse.ArgumentParser(
        description="Usage: ./orbslam_mono_tum path_to_vocabulary path_to_settings path_to_sequence"
    )
    parser.add_argument(
        "vocab_path",
        help="A path to voabulary file from orbslam. \n"
        "E.g: ORB_SLAM/Vocabulary/ORBvoc.txt",
    )
    parser.add_argument(
        "settings_path", help="A path to configurational file, E.g: TUM.yaml"
    )
    parser.add_argument("images_path", help="Path to the folder with images")
    parser.add_argument(
        "--save_map", type=str, default=None, help="a path name to save map to"
    )
    parser.add_argument(
        "--load_map", type=str, default=None, help="path of the map to be loaded"
    )
    parser.add_argument("--start", type=int, default=0, help="Number of starting frame")
    parser.add_argument("--end", type=int, default=None, help="Number of ending frame")
    parser.add_argument("--nth", type=int, default=None, help="use only nth frame")
    parser.add_argument(
        "--reverse", action="store_true", default=False, help="reverse data order"
    )
    args = parser.parse_args()
    vocab_path = args.vocab_path
    settings_path = args.settings_path
    data_tuple = read_folder_as_tuples(args.images_path)
    slam = orbslam2.System(vocab_path, settings_path, orbslam2.Sensor.MONOCULAR)
    slam.set_use_viewer(True)
    slam.initialize()
    slam.osmap_init()
    filenames, timestamps = load_images(args.images_path)
    # slam.activate_localisation_only()
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
        old_timestamps = [kf["mTimeStamp"] for kf in slam.get_keyframe_list()]
        new_ids = [kf["mnId"] for kf in slam.get_keyframe_list()]
    iterator = enumerate(data_tuple[args.start + 1 : end : args.nth])
    if args.reverse:
        iterator = reversed(list(iterator))
    for i, (im, ts) in iterator:
        if args.end and i >= args.end - args.start:
            break
        if i == 0 or i == end - 2:
            time.sleep(0.1)
        else:
            print(i)
            time.sleep(abs(ts - prev_t))
        slam.process_image_mono(im, ts)
        prev_t = ts
    for skf in slam.get_keyframe_list():
        fil_ind = timestamps.index(skf["mTimeStamp"])
        new_ids.append((skf["mnId"], skf["mTimeStamp"], filenames[fil_ind]))
    if args.save_map is not None:
        dump = MapDump(Path(args.save_map), Path("initial_tests"))
        dump.save_osmap(slam)
        dump.save_assoc(
            dict(keyframes=new_ids, data_path=args.images_path, map_name=args.save_map)
        )
