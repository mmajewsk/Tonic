import cv2
import json
import numpy as np


def from_yaml(calibration_file_yaml):
    # @TODO change this when upgrading opencv to > 3.1
    # in 3.1 currently used reading yaml formats is not supported for python
    # values as per https://docs.opencv.org/master/d9/d0c/group__calib3d.html#ga3207604e4b1a1758aa66acb6ed5aa65d
    lines = calibration_file_yaml.readlines()
    camera_lines = list(filter(lambda x: x[:7] == "Camera.", lines))
    assert len(camera_lines) == 11
    dtmp = {}
    for cl in camera_lines:
        data = cl[7:]
        k, v = data.split(":")
        dtmp[k] = float(v)
    mtx_l = [
        [dtmp["fx"], 0, dtmp["cx"]],
        [0, dtmp["fy"], dtmp["cy"]],
        [
            0,
            0,
            1,
        ],
    ]
    mtx = np.array(mtx_l)
    dist = np.array([[dtmp["k1"], dtmp["k2"], dtmp["p1"], dtmp["p2"], dtmp["k3"]]])
    assert dist.shape == (1, 5)
    calib_dict = {"mtx": mtx, "dist": dist}
    return calib_dict


class VideoCalibration:
    def __init__(self, calibration_data, image_shape, new_shape=None):
        """
        Adds calibration_data values as members
        (ret, mtx, dist, rvecs, tvecs)
        :param calibration_data:
        """
        if isinstance(calibration_data, str):
            if calibration_data[-5:] == ".json":
                calibration_data = json.load(open(calibration_data, "r"))
            elif calibration_data[-5:] == ".yaml":
                calibration_data = from_yaml(open(calibration_data, "r"))
            else:
                raise ValueError
        self.mtx = np.array(calibration_data["mtx"])
        self.dist = np.array(calibration_data["dist"])
        self.image_shape = image_shape
        self.new_shape = new_shape
        self.calculate_calibration()

    def calculate_calibration(self):
        w, h = self.image_shape
        if self.new_shape is not None:
            n_w, n_h = self.new_shape
        else:
            n_w, n_h = self.image_shape
        self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(
            self.mtx, self.dist, (w, h), 1, (n_w, n_h)
        )

    def undistort(self, img, use_roi=True):
        img = cv2.undistort(img, self.mtx, self.dist, None, self.newcameramtx)
        if use_roi:
            x, y, w, h = self.roi
            img = img[y : y + h, x : x + w]
        return img

    def action(self, **kwargs):
        return self.undistort(kwargs["img"])


if __name__ == "__main__":
    cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
    cal = VideoCalibration(cal_data, (320, 240))
    dirpath = r"C:\Users\hawker\Dropbox\Public\selfie_car\data_intake3\v1.20"
    import os

    images = os.listdir(dirpath)
    images = filter(lambda x: ".jpg" in x, images)
    images = map(lambda x: os.path.join(dirpath, x), images)
    for img_path in images:
        img = cv2.imread(img_path)
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cal.undistort(img)
        cv2.imshow("img", img)
        cv2.waitKey(20)

    cv2.destroyAllWindows()
