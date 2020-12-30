import cv2
import numpy as np
from logic.calibration import VideoCalibration
import logging

logging.basicConfig(level=logging.DEBUG)

HAXOR_SRC = np.array(
    [
        (100, 146),
        (196, 146),
        (320 - 28, 240 - 23),
        (0 + 12, 240 - 24),
    ]
).astype(np.float32)

HAXOR_SRC2 = np.array(
    [
        (80, 160),
        (216, 160),
        (320 - 28, 240 - 23),
        (0 + 12, 240 - 24),
    ]
).astype(np.float32)
##for rect 2x1


class InversePerspective:
    def __init__(
        self,
        perspective_area=HAXOR_SRC2,
        img_shape=(700, 700),
        desired_shape=(150, 300),
        marigin=12,
    ):
        self.logger = logging.getLogger("inverse_perspective.InversePerspective")
        self.perspective_area = perspective_area
        self.canvas_shape = img_shape
        self.desired_shape = desired_shape
        self.marigin = marigin
        self.img_x_mid = self.desired_shape[0] / 2.0
        self.canvas_x_mid = img_shape[0] / 2.0
        self.roi = None
        self.destination = [
            (
                self.canvas_x_mid - self.img_x_mid,
                img_shape[1] - self.marigin - desired_shape[1],
            ),
            (
                self.canvas_x_mid + self.img_x_mid,
                img_shape[1] - self.marigin - desired_shape[1],
            ),
            (self.canvas_x_mid + self.img_x_mid, img_shape[1] - self.marigin),
            (self.canvas_x_mid - self.img_x_mid, img_shape[1] - self.marigin),
        ]
        self.logger.debug("Setting destination: {}".format(self.destination))
        self.destination = np.array(self.destination).astype(np.float32)
        self.transformation = cv2.getPerspectiveTransform(
            self.perspective_area, self.destination
        )
        self.circle_radius = 3
        self.circle_color = (0, 0, 255)

    def inverse(self, img):
        img = cv2.warpPerspective(img, self.transformation, self.canvas_shape)
        return img

    def calculate_roi_mask(self, roi_polygons=None):
        mask = np.zeros(self.canvas_shape, np.uint8)
        if roi_polygons is None:
            self.roi_polygons = np.array(
                [
                    [
                        (20, 145),
                        (self.canvas_shape[0] - 5, 145),
                        (self.destination[2][0] - 8, mask.shape[1] - 8),
                        (self.destination[3][0] + 8, mask.shape[1] - 8),
                    ]
                ]
            ).astype(np.int32)
        else:
            self.roi_polygons = roi_polygons
        self.logger.debug("Calculating roi: {}".format(self.roi_polygons))
        mask = cv2.fillPoly(mask, self.roi_polygons, 255)
        self.roi = mask

    @property
    def roi_mask(self):
        if not isinstance(self.roi, np.ndarray):
            self.calculate_roi_mask()
        return self.roi

    def _draw_transformation_points(self, img):
        for point in self.perspective_area:
            img = cv2.circle(img, tuple(point), self.circle_radius, self.circle_color)
        return img

    def action(self, **kwargs):
        return self.inverse(kwargs["img"])


if __name__ == "__main__":
    cal_data = r"C:\repositories\autonomic_car\selfie_car\src\pc\settings\camera_calibration\calib.json"
    cal = VideoCalibration(cal_data, (320, 240))
    dirpath = r"C:\repositories\autonomic_car\selfie_car\data_intake4\distance_calib_1"
    marigin = 15
    """
			(102,153),
		(205,153),
		(320-54, 240-15),
		(0+43,240-17),

			(70,169),
		(227,169),
		(320-28, 240-23),
		(0+12,240-24),
	"""
    perspective = InversePerspective()
    import os

    images = os.listdir(dirpath)
    images = filter(lambda x: ".jpg" in x, images)
    images = map(lambda x: os.path.join(dirpath, x), images)
    for img_path in images:
        img = cv2.imread(img_path)
        # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        cv2.imshow("raw", img)
        img = cal.undistort(img)
        img[:135, :, :] = 0
        img_pers = perspective._draw_transformation_points(img.copy())
        _ = perspective.roi_mask
        cv2.imshow("img", img_pers)
        img_uninv = img.copy()
        img = perspective.inverse(img)
        # cv2.imshow('warped',img)
        # print(perspective.roi.dtype)
        for point in perspective.roi_polygons[0]:
            cv2.circle(img, tuple(point), 5, (0, 0, 255), 0)
        cv2.imshow("maskpoints", img)
        img = cv2.bitwise_and(img, img, mask=perspective.roi_mask)
        cv2.imshow("masked", img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
