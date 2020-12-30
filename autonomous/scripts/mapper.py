from argparse import ArgumentParser
import cv2
from logic.mapper import Mapper2
from logic.calibration import VideoCalibration
import numpy as np
from scipy.spatial import transform
from common.slam_map import OsmapData
from common.pose import (
    Transform3Dto2D,
    Pose3DtoWorld,
    destination_to_angle,
    data_iterator,
)
from logic.inverse_perspective import InversePerspective


HAXOR_SRC3 = np.array(
    [
        (80, 160),
        (216, 160),
        (320 - 28, 240 - 23),
        (0 + 12, 240 - 24),
    ]
).astype(np.float32)

if __name__ == "__main__":
    ## @MentalMap
    # Calibration is needed to undistort
    # Perspective reverses the image
    parser = ArgumentParser()
    parser.add_argument("calibration", help="path to json calibration file")
    parser.add_argument("map_path", help="path to maps yaml file")
    parser.add_argument("images_path", help="path to folder with images")
    #'/home/mwm/Desktop/datadumps/01-07-19-drive-v1_22'
    parser.add_argument("assoc_file", help="path to assoc.json file")
    #'./assets/maps/testmap1/assoc.json'
    args = parser.parse_args()
    img_shape = 320, 240
    calibration = VideoCalibration(args.calibration, img_shape, new_shape=img_shape)
    mapper = Mapper2(
        map_shape=(800, 800, 3),
        coord_coef=((50, 400), (150, 400)),
        rot_cent_coef=((0.5, 0), (1.1, 0)),
        type="additive",
    )
    perspective = InversePerspective(
        perspective_area=HAXOR_SRC3,
        img_shape=(250, 250),
        desired_shape=(100, 130),
        marigin=0.25,
    )
    perspective.calculate_roi_mask()
    my_osmap = OsmapData.from_map_path(args.map_path)
    id_and_pose = my_osmap.id_and_pose()
    transformator = Transform3Dto2D(my_osmap)
    to_world = Pose3DtoWorld()
    # @TODO fix this, this is an issue of calibration not being accurate enough
    calibration.dist[0, 1] = 0.12
    calibration.calculate_calibration()
    print("new dst", calibration.dist)
    print("roi", calibration.roi)
    mask = np.zeros(perspective.canvas_shape, np.uint8)
    a = 20
    b = 165
    polygon = np.array(
        [
            [
                (a, b),
                (perspective.canvas_shape[0] - a, b),
                (perspective.destination[2][0] - 8, mask.shape[1] - 8),
                (perspective.destination[3][0] + 8, mask.shape[1] - 8),
            ]
        ]
    ).astype(np.int32)
    print(polygon)
    perspective.calculate_roi_mask(polygon)
    for kf_id, pose, ts, filename, img in data_iterator(
        id_and_pose, args.images_path, args.assoc_file
    ):
        if True:
            undi = calibration.undistort(img, use_roi=True)
            undi[:100, :, :] = 0
            cv2.imshow("preinv", undi)
            img = perspective.inverse(undi)

            img = cv2.bitwise_and(img, img, mask=perspective.roi_mask)
            cv2.imshow("persp", img)
            cv2.waitKey(0)
        pose_world = to_world(pose)
        position, normal_vec = transformator(pose_world)
        position = position[:2]
        angle = destination_to_angle(position, normal_vec)
        offset_position = np.array((position[0], position[1]))
        mapper.update(img, angle=180 + np.rad2deg(angle), position=offset_position)
        cv2.imshow("map", mapper.map)
        cv2.waitKey(0)
