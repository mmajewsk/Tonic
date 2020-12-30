import numpy as np
import osmap_pb2
import pathlib


class KeyFrame:
    pass

class KeyFrameArray:
    def __init__(self):
        self.array = None

    @staticmethod
    def from_protobuf(self, protobuf_key_frame_array):
        new_array = KeyFrameArray()
        new_array.array = []
        for keyframe in protobuf_key_frame_array:
            self.array.append(KeyFrame.from_protobuf(keyframe))

def read_map_data(main_path, filename, data_type):
    dataCLASS = {
            'mappoints': osmap_pb2.SerializedMappointArray,
            'keyframes': osmap_pb2.SerializedKeyframeArray,
            'features': osmap_pb2.SerializedKeyframeFeaturesArray,
            }
    read_path = main_path/'{}.{}'.format(filename, data_type)
    with open(read_path, 'rb') as a :
            _data = dataCLASS[data_type]()
            _data.ParseFromString(a.read())
    return _data

class OsmapData:
    def __init__(self, key_frame, map_points, features, map_path=None, map_name=None):
        self.key_frames = key_frame
        self.map_points = map_points
        self.features = features
        self.map_path = map_path
        self.map_name = map_name

    @staticmethod
    def from_map_path( map_path):
        map_path = pathlib.Path(map_path)
        path, map_name = map_path.parent, map_path.stem
        key_frames = read_map_data(path, map_name, 'keyframes')
        map_points = read_map_data(path, map_name, 'mappoints')
        features = read_map_data(path, map_name, 'features')
        return OsmapData(key_frames, map_points, features, map_path=path, map_name=map_name)

    def keyframe_to_pose(self, kf):
        pose = list(kf.pose.element)
        reshaped_pose = np.array(pose).reshape(3,4)
        pose_base = np.eye(4)
        pose_base[:3] = reshaped_pose
        return pose_base

    def id_and_pose(self):
        return [(kf.id, self.keyframe_to_pose(kf)) for kf in self.key_frames.keyframe ]

    def poses_reshaped(self):
        return [self.keyframe_to_pose(kf) for kf in self.key_frames.keyframe]

    def paint_data(self):
        poses = []
        points = []
        for kf in self.key_frames.keyframe:
            pose_base = self.keyframe_to_pose(kf)
            poses.append(pose_base)
        for p in self.map_points.mappoint:
            position = p.position
            points.append(np.array([position.x, position.y, position.z]))
        return poses, points



