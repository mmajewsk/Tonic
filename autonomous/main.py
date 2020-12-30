import sys
import time
from common.pose import Pose3Dto2D, transform, Transform3Dto2D
import logging
from logging.handlers import RotatingFileHandler
import cv2
from matplotlib import pyplot as plt
from tonic import Tonic
import numpy as np
from common.slam_map import OsmapData
from tonic_autonomous.mocks import TonicMock, DriverMock
from tonic_autonomous.navigation import Navigator
from tonic_autonomous.localisation import Localisator
from tonic_autonomous.driver import DriverDumb
from tonic_autonomous.vis import Visualisation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler(
    "direction_finding.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=0,
)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s][%(funcName)s]%(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


import timeit

if __name__ == "__main__":
    vocab_path = "/home/mwm/repositories/slam_dunk/builds/data/ORBvoc.txt"
    settings_path = "/home/mwm/repositories/os2py_applied/TUM-MINE-wide.yaml"  # "./assets/settings/TUM-MINE-wide.yaml "
    images_path = "/home/mwm/repositories/TonicData/19_11_2020_home_v0.3"

    # checkpoints_file = "/home/mwm/repositories/Tonic/autonomous/assets/checkpoints/checkpoints_home_27_07_2020v2.txt"
    # /home/mwm/repositories/Tonic/autonomous/assets/checkpoints/to_fridge
    checkpoints_dir = (
        "/home/mwm/repositories/Tonic/autonomous/assets/checkpoints/back_fridge_prev"
    )
    osmap_path = "/home/mwm/repositories/Tonic/autonomous/assets/maps/home_19_11_2020_map1_s1120/initial_tests.yaml"
    # tonic_settings = "/home/mwm/repositories/Tonic/remote_control/settings.yaml"
    tonic_settings = "/home/mwm/repositories/Tonic/control/settings.yaml"
    mock = True
    visualise = True
    if mock:
        tonic = TonicMock(images_path, start=500)
    else:
        tonic = Tonic(tonic_settings)
        tonic.connect_video()
    print("wait for camera to start")
    image = None
    while image is None:
        time.sleep(2)
        initialising_data = tonic.image_now()
        image = initialising_data[0]
    my_osmap = OsmapData.from_map_path(osmap_path)
    # this below is needed to calculate the 2D surface
    transformator = Transform3Dto2D(my_osmap)
    # navigator = Navigator.from_txt(checkpoints_file, orb_slam_map=my_osmap)
    navigator = Navigator.from_dir(checkpoints_dir, orb_slam_map=my_osmap)
    navigator.set_smart_threshold(0.4)
    localisator = Localisator(
        tonic=tonic, vocab_path=vocab_path, settings_path=settings_path
    )
    logger.debug("initialising localisator")
    localisator.initialise(initialising_data, my_osmap)
    # if mock:
    #    driver = DriverMock(tonic)
    # else:
    logger.debug("starting driver")
    driver = DriverDumb(tonic)
    start = time.time()
    start_time = timeit.default_timer()
    if visualise:
        vis2d = Visualisation(transformator)
        vis2d.add_navigator(navigator)
    print("Start navigating")
    navigator.register_signal(driver.navigator_queue)
    for destination in navigator.go():
        data = tonic.image_now()
        current_im, ts = data
        pose3D = localisator.localise(data)
        if pose3D is not None:
            current_pose2D = transformator(pose3D)
        else:
            current_pose2D = None
        destination2D = transformator(destination)
        if current_pose2D is not None and visualise:
            vis2d.set_3d(pose3D, destination)
            vis2d.set_2d(current_pose2D, destination2D)
            vis2d.visualize()
        driver.drive(current_pose2D, destination2D)
        navigator.refresh_direction(pose3D)
        if time.time() - start > 300:
            localisator.slam.shutdown()
            sys.exit()
