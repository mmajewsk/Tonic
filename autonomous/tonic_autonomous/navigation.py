import json
from collections import deque
import logging
import time
import numpy as np
import os
from common.pose import Pose3DtoWorld

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Navigator:
    to_world = Pose3DtoWorld()

    def __init__(self, checkpoints: deque, distance_threshold=None):
        """

        :param checkpoints: list of 3D poses we want to go through, in a world frame of reference
        """
        self.distance_threshold = distance_threshold
        self.checkpoints = checkpoints
        self.target_pose = None
        self.finish = False
        self._signals = []

    @staticmethod
    def from_txt(checkpoints_filepath, orb_slam_map):
        with open(checkpoints_filepath, "r") as f:
            filenames_list = f.read().splitlines()
        return Navigator.from_filenames(filenames_list, orb_slam_map)

    @staticmethod
    def from_dir(checkpoints_folder, orb_slam_map):
        """
        It only uses sorted checkpoints
        """
        filenames_list = sorted(os.listdir(checkpoints_folder))
        return Navigator.from_filenames(filenames_list, orb_slam_map)

    @staticmethod
    def from_filenames(filenames_list, orb_slam_map):
        with open(orb_slam_map.map_path / "assoc.json", "r") as f:
            assoc_dict = json.load(f)
        assoc_keyframes = filter(lambda x: isinstance(x, list), assoc_dict["keyframes"])
        assoc_filenames = {filename: id for id, timestamp, filename in assoc_keyframes}
        for checkpoint_filename in filenames_list:
            if checkpoint_filename not in assoc_filenames:
                raise ValueError(
                    "checkpoint_filename {} was not found in keyframes".format(
                        checkpoint_filename
                    )
                )
        id_and_pose = {id: pose for id, pose in orb_slam_map.id_and_pose()}
        checkpoints = deque()
        for checkpoint_filename in filenames_list:
            checkpoint_keyframe_id = assoc_filenames[checkpoint_filename]
            pose = id_and_pose[checkpoint_keyframe_id]
            pose = Navigator.to_world(pose)
            checkpoints.append(pose)
        return Navigator(checkpoints)

    def set_smart_threshold(self, fraction=0.2):
        distances = []
        tmp_deq = self.checkpoints.copy()
        prev = tmp_deq.popleft()
        for checkpoint in tmp_deq:
            distances.append(self.distance(prev, checkpoint))
            prev = checkpoint
        mean_checkpoint_distance = np.mean(distances)
        self.distance_threshold = fraction * mean_checkpoint_distance

    def register_signal(self, queue):
        self._signals.append(queue)

    def signals(self, message):
        for q in self._signals:
            q.put(message)

    def go(self):
        while not self.finish:
            if self.target_pose is None:
                self.target_pose = self.checkpoints[0]
            yield self.target_pose

    def get_checkpoint(self, a):
        return 't'

    def refresh_direction(self, current_position):
        if current_position is None:
            pass
        else:
            distance = self.distance(current_position, self.target_pose)
            if distance < self.distance_threshold:
                logger.debug(
                    "Witihin range (distance: {}) of checkpoint of {}".format(
                        distance, self.target_pose
                    )
                )
                if len(self.checkpoints) == 0:
                    self.finish = True
                    self.signals(("finish", time.time()))
                else:
                    self.target_pose = self.checkpoints.popleft()
                    self.signals(("checkpoint_reached", time.time()))
                    logger.debug(
                        "Left checkpoints: {}. Changing to checkpoint {}".format(
                            len(self.checkpoints), self.target_pose
                        )
                    )

    def distance(self, pose_a, pose_b):
        return np.linalg.norm(pose_a[:2, 3] - pose_b[:2, 3])
