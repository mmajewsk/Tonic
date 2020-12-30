import cv2
import numpy as np
from scipy.integrate import cumtrapz


def retrofit_slice(series, start, stop):
    error = np.arange(stop - start)
    error = error / (1.0 * error[-1])
    pedestal = series.loc[stop]
    error = error * pedestal
    series.loc[start : stop - 1] -= error
    series.loc[stop:] -= pedestal
    return series, error, pedestal


def integrate(df, target="vel_x", source="gyr_x"):
    cumtrapz_result = cumtrapz(df[source].values, df["alltimes"].values)
    # print(df.loc[1:, target].shape,cumtrapz_result.shape)
    df.loc[1:, target] = cumtrapz_result
    df.loc[0, target] = df.loc[1, target]
    return df


def fix_drift(df, column):
    for i, rows in df.iterrows():
        value = df[column].loc[i]
        # print(bool(rows['stop']),bool(df['stop'].iloc[i-1]))
        if rows["stop"] == 0 and df["stop"].iloc[i - 1] != 0:
            start = i
        elif rows["stop"] != 0 and df["stop"].iloc[i - 1] == 0:
            # fig = plt.figure()
            # ax1 = fig.add_subplot(111)
            # ax1.plot(df[column].index, df[column], color='green')
            stop = i
            series, error, pedestal = retrofit_slice(df.loc[:, column], start, stop)
            df.loc[:, column] = series
        # ax1.plot(df[column].index, df[column], color='blue')
        # ax1.plot(series[start:stop].index, error, color='red')
        # print(pedestal)
        if rows["stop"] != 0:
            df[column][i:] -= value
            df.set_value(i, column, 0.0)
    return df


def Mapper(*args, **kwargs):
    from warnings import warn

    warn("This class ios deprecated! Use Mapper2")
    return OldMapper(*args, **kwargs)


class Mapping:
    def convert(self, point: tuple):
        pass


class LinearMapping(Mapping):
    def __init__(self, x_coef, y_coef):
        Mapping.__init__(self)
        self.x_coef = x_coef
        self.y_coef = y_coef
        linear_func = lambda coef, val: coef[0] * val + coef[1]
        self.apply_x = lambda val: linear_func(self.x_coef, val)
        self.apply_y = lambda val: linear_func(self.y_coef, val)
        self.apply = lambda point: (self.apply_x(point[0]), self.apply_y(point[1]))

    def convert(self, point: tuple):
        return self.apply(point)


class Mapper2:
    def __init__(
        self,
        map_shape=(800, 800, 3),
        coord_coef=((100, 400), (150, 400)),
        rot_cent_coef=((0.5, 0), (1.1, 0)),
        type="show_only",
    ):
        assert type in ["show_only", "additive"]
        self.map_type = type
        self.map_size = map_shape[:2]
        self.map_shape = map_shape
        self._map = np.zeros(self.map_shape, dtype=np.uint8)
        # This one transforms x,y position from real world
        # to position on created map
        self.coordinates_mapping = LinearMapping(*coord_coef)
        # Sets the center based on the shape of the image
        self.rotation_center_mapping = LinearMapping(*rot_cent_coef)
        self.base = None
        self.resize_img = lambda x: cv2.resize(x, (0, 0), fx=0.4, fy=0.4)

    @property
    def blanc(self):
        # @TODO fix the shape to be color
        return np.zeros(self.map_shape[:2], np.uint8)

    def set_rotation_center_mapping(self, mapping: Mapping):
        self.rotation_center_mapping = mapping

    @property
    def map(self):
        return self._map

    def get_base(self):
        if self.base is None:
            self.base = np.zeros(self.map_shape, np.uint8)
        if self.map_type == "show_only":
            return self.blanc
        elif self.map_type == "additive":
            return self.base

    def set_mapping(self, mapping: Mapping):
        self.coordinates_mapping = mapping

    def rotate_image(self, frame, angle: float):
        """
        So how this works:
        1. get center of rotation
        2. calc matrix
        3. process to gray
        4. warp, into shape of the MAP SIZE
        """
        center_of_rotation = self.rotation_center_mapping.apply(frame.shape[:2])
        center_of_rotation = tuple(map(int, center_of_rotation))
        frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        canvas = self.blanc
        y_origin = canvas.shape[0] / 2 - frame.shape[0] / 2
        x_origin = canvas.shape[1] / 2 - frame.shape[1] / 2
        y_origin, x_origin = map(int, (y_origin, x_origin))
        canvas[
            y_origin : y_origin + frame.shape[0], x_origin : x_origin + frame.shape[1]
        ] = frame
        canvas_cor = center_of_rotation[0] + y_origin, center_of_rotation[1] + x_origin
        rot = cv2.getRotationMatrix2D(canvas_cor, angle, scale=1)
        dst = cv2.warpAffine(canvas, rot, self.map_size)
        return dst, canvas_cor

    def position_after_rotation(self, img, center_of_rotation):
        # cut patch out of the image afer rotation
        # return this patch and on-patch coordinates of center of rotation
        thresh = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        c = max(cnts, key=cv2.contourArea)
        left = tuple(c[c[:, :, 0].argmin()][0])
        right = tuple(c[c[:, :, 0].argmax()][0])
        top = tuple(c[c[:, :, 1].argmin()][0])
        bottom = tuple(c[c[:, :, 1].argmax()][0])

        image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        cv2.circle(image, left, 8, (0, 50, 255), -1)
        cv2.circle(image, right, 8, (0, 255, 255), -1)
        cv2.circle(image, top, 8, (255, 50, 0), -1)
        cv2.circle(image, bottom, 8, (255, 255, 0), -1)
        cv2.imshow("d", image)
        cv2.waitKey(0)
        cor_y, cor_x = center_of_rotation
        left_x, left_y = left
        right_x, right_y = right
        top_x, top_y = top
        bottom_x, bottom_y = bottom
        patch_left_x = min((cor_x, left_x, right_x))
        patch_right_x = max((cor_x, left_x, right_x))
        # below min and max are inverted because Y grows towards bottom
        patch_top_y = min((cor_y, top_y, bottom_y))
        patch_bottom_y = max((cor_y, top_y, bottom_y))
        patch = img[patch_top_y:patch_bottom_y, patch_left_x:patch_right_x]
        patch_origin = patch_top_y, patch_left_x
        on_patch_cor = np.array(center_of_rotation) - np.array(patch_origin)
        assert np.all(on_patch_cor >= 0)

        return patch, on_patch_cor, patch_origin

    def update(self, frame, angle=0.0, position=(0, 0)):
        """
        :param frame:
        :param angle: float of degrees
        :param position:
        :return:
        """
        img = self.resize_img(frame)
        self.on_screen_position = self.coordinates_mapping.convert(position)
        self.on_screen_position_int = tuple(map(int, self.on_screen_position))
        # @TODO fix this to be color
        if self.base is None:
            self.base = np.zeros((800, 800), np.uint8)
        base = self.get_base()
        dst, cor = self.rotate_image(img, angle)
        patch, on_patch_cor, patch_origin = self.position_after_rotation(dst, cor)
        on_screen_position_arr = np.array(self.on_screen_position_int)
        on_screen_patch_pos = on_screen_position_arr - on_patch_cor
        final_img = self.blanc
        final_img[
            on_screen_patch_pos[0] : on_screen_patch_pos[0] + patch.shape[0],
            on_screen_patch_pos[1] : on_screen_patch_pos[1] + patch.shape[1],
        ] = patch
        self._last_dst = final_img
        self._map = Mapper2.merge_images(self._last_dst, base)
        self.base = self._map.copy()

    @staticmethod
    def get_image_overlap_masks(img1, img2):
        ret, white_on_1 = cv2.threshold(img1, 1, 255, cv2.THRESH_BINARY)
        black_on_1 = ~white_on_1
        ret, white_on_2 = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)
        common_mask = cv2.bitwise_and(white_on_1, white_on_2)
        only_2_mask = cv2.bitwise_and(black_on_1, ~common_mask)
        only_1_mask = cv2.bitwise_and(white_on_1, ~common_mask)
        return only_1_mask, common_mask, only_2_mask

    @staticmethod
    def get_image_overlap_areas(img1, img2):
        new_image_mask, common_mask, base_mask = Mapper2.get_image_overlap_masks(
            img1, img2
        )
        img2_only = cv2.bitwise_or(img2, img2, mask=base_mask)
        img1_only = cv2.bitwise_or(img1, img1, mask=new_image_mask)
        common_2 = cv2.bitwise_or(img2, img2, mask=common_mask)
        common_1 = cv2.bitwise_or(img1, img1, mask=common_mask)
        return img1_only, common_1, common_2, img2_only

    @staticmethod
    def merge_images(new_img, base):
        base_orig = base.copy()
        (
            only_new_img,
            common_1,
            common_2,
            only_base_img,
        ) = Mapper2.get_image_overlap_areas(new_img, base_orig)
        common_img = cv2.addWeighted(common_2, 0.5, common_1, 0.5, 0.0)
        new_map = cv2.add(
            only_base_img, only_new_img
        )  # paste whats dark in present, and white in past
        new_map = cv2.add(new_map, common_img)
        return new_map
