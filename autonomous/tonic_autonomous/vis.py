from tonic_autonomous.navigation import Navigator
import numpy as np
from common.pose import destination_to_angle
import cv2


class Visualisation:
    def __init__(self, transformator):
        self.navigator = None
        self.transformator = transformator
        self.initiated = False
        self._buffer = None
        self._size = 512
        self.make_background = lambda: np.zeros((self._size, self._size, 3), np.uint8)

        self.to_screen_transform = None

    def add_navigator(self, navigator: Navigator):
        self.navigator = navigator

    def draw_checkpoint(self, point):
        cv2.circle(self._buffer, tuple(point), 15, (0, 0, 255))

    def draw_checkpoints(self, checkpoints):
        for p in checkpoints:
            self.draw_checkpoint(p)

    def draw_destination(self, p):
        cv2.circle(self._buffer, tuple(p), 15, (255, 0, 0), -1)

    def draw_car(self, p, p2, p3):
        cv2.circle(self._buffer, tuple(p), 10, (0, 255, 0))
        cv2.line(self._buffer, tuple(p), tuple(p2), (0, 255, 0), 3)
        cv2.line(self._buffer, tuple(p), tuple(p3), (255, 0, 0), 3)

    def calculate_transformation(self, objects, factor=2):
        d_x, d_y = np.array(objects).T
        xmin, xmax = min(d_x), max(d_x)
        ymin, ymax = min(d_y), max(d_y)
        xlen = factor * abs(xmax - xmin)
        ylen = factor * abs(ymax - ymin)
        w_factor = 1.2
        self.window_size = max(xlen, ylen) * w_factor
        border = (w_factor - 1) / 2
        window_shift = (
            -xmin + border * self.window_size,
            -ymin + border * self.window_size,
        )
        scale = self._size / self.window_size
        return lambda p: np.array(
            ((p[0] + window_shift[0]) * scale, (p[1] + window_shift[1]) * scale),
            dtype=int,
        )

    def set_2d(self, pose, destination):
        self.current2d = pose
        self.destination2d = destination

    def set_3d(self, pose, destination):
        self.current3d = pose
        self.destination3d = destination

    def visualize(self):
        self._buffer = self.make_background()
        checkpoints = [
            self.transformator(checkpoint)[0]
            for checkpoint in self.navigator.checkpoints
        ]
        checkpoints.append(self.destination2d[0])
        all_objects = [ckp for ckp in checkpoints]
        all_objects.append(self.current2d[0])
        if self.to_screen_transform is None:
            self.to_screen_transform = self.calculate_transformation(all_objects)
        checkpoints_on_screen = [
            self.to_screen_transform(checkpoint) for checkpoint in checkpoints
        ]
        self.draw_checkpoints(checkpoints_on_screen)
        destination_on_screen = self.to_screen_transform(self.destination2d[0])
        self.draw_destination(destination_on_screen)
        x, y = self.current2d[0]
        l = 0.05 * self.window_size
        angle = destination_to_angle(self.current2d[0], self.destination2d[0])
        u = x + l * np.cos(angle)
        v = y + l * np.sin(angle)
        curr_ang = destination_to_angle(self.current2d[0], self.current2d[1], flip=True)
        k = x + l * np.cos(curr_ang)
        m = y + l * np.sin(curr_ang)
        current_on_screen = self.to_screen_transform(self.current2d[0])
        uv = self.to_screen_transform((u, v))
        km = self.to_screen_transform((k, m))
        self.draw_car(current_on_screen, uv, km)
        # print("=======================")
        # print(self.current3d)
        # print(self.current3d.dot(self.transformator.pose_transformer.transform))
        # print(self.transformator.pose_transformer.transform.dot(self.current3d))
        # print(self.current2d)
        # print("=======================")
        # print(
        #     "On screen: Current [{}] Destination [{}] Angle[{}]".format(
        #         current_on_screen, destination_on_screen, angle
        #     )
        # )
        # print(
        #     "In 2D: Current [{}] Destination [{}] Angle[{}]".format(
        #         current, destination, angle
        #     )
        # )
        # print()
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.4
        color = (0, 0, 255)
        thickness = 1
        org = (30, 20)
        text = "screen: c [{}] d[{}] a [{}]".format(
            current_on_screen, destination_on_screen, np.rad2deg(angle)
        )
        text = "world: c [{cx:.3f},{cy:.3f}] d [{dx:.3f},{dy:.3f}] a [{a:.3f}]".format(
            cx=self.current2d[0][0],
            cy=self.current2d[0][1],
            dx=self.destination2d[0][0],
            dy=self.destination2d[0][1],
            a=np.rad2deg(angle),
        )
        self._buffer = cv2.putText(
            self._buffer, text, org, font, fontScale, color, thickness, cv2.LINE_AA
        )
        cv2.imshow("vis", self._buffer)
        cv2.waitKey(30)


if __name__ == "__main__":
    pass
