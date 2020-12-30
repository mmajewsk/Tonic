import os
from scipy.spatial import transform
import numpy as np
import json
import cv2
import pathlib
from common.slam_map import OsmapData


class Pose3DtoWorld:
    def __init__(self):
        self.reprojector = lambda x: -x.T @ x[:, 3]

    def __call__(self, pose):
        p = self.reprojector(pose)
        pose[:, 3] = p
        return pose


class Pose3Dto2D:
    def __init__(self, poses):
        coords = self.poses_to_coords(poses)
        plane_normal_vector = self.calculate_plane(coords)
        self.rotation = self.rotation_vector_to_z(plane_normal_vector)
        pose_transform = np.eye(4)
        pose_transform[:3, :3] = self.rotation.as_dcm()
        self.transform = pose_transform

    def poses_to_coords(self, poses):
        coords = [pose[:3, 3] for pose in poses]
        return np.array(coords)

    def calculate_plane(self, coords):
        """

        :param coords: np array [[x1,y1,z1], ..., [xn,yn,zn]]
        :return: normal vector to the plane
        """
        G = coords.sum(axis=0) / coords.shape[0]
        u, s, vh = np.linalg.svd(coords - G)
        u_norm = vh[2, :]
        return u_norm

    def rotation_vector_to_z(self, normal_vector) -> transform.Rotation:
        xrot = np.zeros_like(normal_vector)
        yrot = np.zeros_like(normal_vector)
        # first step, get rid of x axis, and look only at y,z
        # calculate the angle between the 2D vector in that plane
        # and the vector pointing up in z
        desired_vector = [0, 1]
        # this is because dot product of v1 * v2 = ||v1||*||v2||*cos(alpha)
        # and ||v1|| in both cases are almost 1
        yz_vector = normal_vector[1:]
        xrot[0] = np.arccos(
            (yz_vector.dot(desired_vector)) / np.linalg.norm(yz_vector)
        )  # np.arctan(-normal[1]/normal[2])
        # -xrot, because we want to reverse this operation
        rotx = transform.Rotation.from_euler("xyz", -xrot)
        newax = rotx.as_dcm().dot(normal_vector)
        xz_vector = newax[[0, 2]]
        yrot[1] = np.arccos((xz_vector.dot([0, 1])) / np.linalg.norm(xz_vector))
        tot_rot = -xrot - yrot
        return transform.Rotation.from_euler("xyz", tot_rot)


def ts_fname_association_to_id(assoc_path):
    with open(assoc_path, "r") as f:
        json_img_assoc = json.loads(f.read())
    img_assoc_dict = {t[0]: (t[1], t[2]) for t in json_img_assoc["keyframes"]}
    return img_assoc_dict


def data_iterator(id_and_pose, images_path, assoc_path):
    img_assoc_dict = ts_fname_association_to_id(assoc_path)
    data_path = pathlib.Path(images_path)
    for kf_id, pose in id_and_pose:
        ts, filename = img_assoc_dict[kf_id]
        img = cv2.imread(str(data_path / filename))
        yield kf_id, pose, ts, filename, img


class Transform3Dto2D:
    def __init__(self, my_osmap):
        self.pose_transformer = Pose3Dto2D(my_osmap.poses_reshaped())

    def __call__(self, pose):
        # if pose[0, 3] <= 0:
        #     pose[0, 3] = -pose[0, 3]
        flat_pose = self.pose_transformer.transform.dot(pose)

        looking_direction = pose.copy()
        looking_direction[:3, 3] = looking_direction[:3, 3] + np.array([0, 0, 1])
        looking_direction[:3, 3] = pose[:3, :3] @ looking_direction[:3, 3]

        # new_angles = transform.Rotation.from_dcm(new_pose[:3, :3]).as_euler("xyz")
        position = flat_pose[:2, 3]
        normal_vector = self.pose_transformer.transform.dot(looking_direction)
        norm_v = normal_vector[:2, 3]  # - position
        # print("lormak     ===== ", norm_v)
        # print("pos     ===== ", position)
        return position, norm_v


def destination_to_angle(current, destination, flip=False):
    (x1, y1) = current
    (x2, y2) = destination
    a = x2 - x1
    b = y2 - y1
    angle = np.arctan2(b, a)
    if flip:
        angle = np.pi - angle
    return angle
