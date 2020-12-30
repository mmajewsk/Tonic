from ..slam_map import OsmapData
import io
import random
import json
import numpy as np
import pickle
import collections
import cv2
import pathlib
from collections import defaultdict

def redistort_points(mtx, distCoeff, undist_points, imsize):
    ptsOut = undist_points
    ptsTemp = np.array([], dtype='float32')
    rtemp = ttemp = np.array([0,0,0], dtype='float32')
    ptsOut = cv2.undistortPoints(ptsOut, mtx, None)
    ptsTemp = cv2.convertPointsToHomogeneous( ptsOut )
    output = cv2.projectPoints( ptsTemp, rtemp, ttemp, mtx, distCoeff, ptsOut )
    return output

def read_calibration(calibration_data_path):
    with open(calibration_data_path) as ff:
        calib = json.loads(ff.read())
        mtx = np.array(calib['mtx'])
        distCoeff = np.array(calib['dist'])
    return mtx, distCoeff

def read_assoc(assoc_path):
    with open(assoc_path, 'r') as f:
        json_img_assoc = json.loads(f.read())
        img_assoc_dict = { t[0]: (t[1],t[2]) for t in json_img_assoc['keyframes']}
    return img_assoc_dict

# Draw delaunay triangles
def extract_triangles(subdiv):
    triangleList = subdiv.getTriangleList();
    triangles = []
    for t in triangleList:
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])
        triangles.append((pt1,pt2,pt3))
    return triangles


def draw_delaunay(img, subdiv, delaunay_color ) :
    size = img.shape
    r = (0, 0, size[1], size[0])
    triangles = extract_triangles(subdiv)
    for pt1, pt2, pt3 in triangles :
        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
            cv2.line(img, pt1, pt2, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt2, pt3, delaunay_color, 1, cv2.LINE_AA, 0)
            cv2.line(img, pt3, pt1, delaunay_color, 1, cv2.LINE_AA, 0)


# Draw voronoi diagram
def draw_voronoi(img, subdiv) :

    ( facets, centers) = subdiv.getVoronoiFacetList([])

    for i in range(0,len(facets)) :
        ifacet_arr = []
        for f in facets[i] :
            ifacet_arr.append(f)

        ifacet = np.array(ifacet_arr, np.int)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        cv2.fillConvexPoly(img, ifacet, color, cv2.LINE_AA, 0);
        ifacets = np.array([ifacet])
        cv2.polylines(img, ifacets, True, (0, 0, 0), 1, cv2.LINE_AA, 0)
        cv2.circle(img, (centers[i][0], centers[i][1]), 3, (0, 0, 0), cv2.FILLED, cv2.LINE_AA, 0)


# Check if a point is inside a rectangle
def rect_contains(rect, point) :
    if point[0] < rect[0] :
        return False
    elif point[1] < rect[1] :
        return False
    elif point[0] > rect[2] :
        return False
    elif point[1] > rect[3] :
        return False
    return True

# Draw a point
def draw_point(img, p, color ) :
    cv2.circle( img, p, 2, color, cv2.cv.CV_FILLED, cv2.CV_AA, 0 )

def get_distorted_image_features(my_osmap, kfid, shape):
    for kf in my_osmap.features.feature:
        if kf.keyframe_id == kfid:
            framepoints = [[(feat.keypoint.ptx, feat.keypoint.pty, feat.mappoint_id)  for feat in kf.feature if feat.mappoint_id!=0]]
            fps_np = np.array(framepoints)
            distorted = redistort_points(mtx, distCoeff, fps_np[:,:,:2], shape)
            fps_np[0,:,:2] = distorted[0]
            return fps_np.astype(np.float32)
    return None

def fill_subdiv(fps_np, subdiv, size):
    for px, py, mapid in fps_np[0]:
        boundary = 30
        if boundary<px<size[1]-boundary and boundary<py<size[0]-boundary:
            subdiv.insert((px,py))

def get_cropped_triangle(img, triangle):
    size = img.shape
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    fits_rect = lambda x: 0<x[0]<size[1] and 0<x[1]<size[0]
    condition = list(map(fits_rect, triangle))
    if not all(condition):
        return None
    triangle = np.array(list(triangle), 'int32')
    cv2.fillConvexPoly(mask, triangle, (255))
    #cv2.drawContours(mask, [triangle], -1, (255, 255, 255), -1, cv2.LINE_AA)
    res = cv2.bitwise_and(img,img,mask = mask)
    return res

def get_cropped_roi_square(img, triangle):
    triangle_cropped = get_cropped_triangle(texture_image, triangle_dict['triangle'])
    rect = cv2.boundingRect(np.array(triangle_dict['triangle']))
    x,y,w,h = rect
    a = max(h,w)
    square = np.zeros(shape=(a,a,triangle_cropped.shape[2]), dtype=triangle_cropped.dtype)
    cut_square = triangle_cropped[y:y+h, x:x+w]
    square[0:h, 0:w] = cut_square
    return square

def mnids_to_triangles(my_osmap, data_path, img_assoc_dict):
    triangles3d = defaultdict(list)
    # key: sorted((mnid1, mnid2, mnid3))
    # value: [
    #         {
    #          img:filename,
    #          kfid:int,
    #          #crop:np.array,
    #          mnidlist: [mnid1, mnid2, mnid3]
    #          triangle: [p1,p2,p3],
    #         },
    #        {...},
    #        ...,
    #        {...}
    #        ]
    for kf in my_osmap.key_frames.keyframe:
        kfid = kf.id
        print("Processing ", kfid)
        ts, filename = img_assoc_dict[kf.id]
        img = cv2.imread(str(data_path/filename))
                #for kp in distorted[0][0]:
        #   cv2.circle(img,(int(kp[0]), int(kp[1])), 3, (255,0,0))
        fps_np = get_distorted_image_features(my_osmap, kfid, img.shape)
        size = img.shape
        rect = (0, 0, size[1], size[0])
        subdiv  = cv2.Subdiv2D(rect)
        fill_subdiv(fps_np, subdiv, size)
        triangles = extract_triangles(subdiv)
        point_to_map_id = {}
        for px, py, mnid in fps_np[0,:,:]:
            point_to_map_id[(px,py)] = mnid
        triangles_as_map_ids = {}
        triangles_as_crop = {}
        for p1,p2,p3 in triangles:
            crop_triangle = get_cropped_triangle(img, (p1,p2,p3))
            triangles_as_crop[(p1,p2,p3)] = crop_triangle
            mnid1 = point_to_map_id.get(p1)
            mnid2 = point_to_map_id.get(p2)
            mnid3 = point_to_map_id.get(p3)
            if mnid1 is not None and mnid2 is not None and mnid3 is not None:
                mnidlist = (mnid1, mnid2, mnid3)
                triangle_mnids = tuple(sorted(mnidlist))
                pointlis = [list(p1),list(p2),list(p3)]
                triangles3d[triangle_mnids].append({
                    "img": filename,
                    "kfid": kfid,
                    #"crop": crop_triangle,
                    "mnidlist": list(mnidlist),
                    "triangle": pointlis
                    })

        #draw_delaunay(img, subdiv, (255,0,0))
        #draw_voronoi(img, subdiv)
        #cv2.imshow('cut',crop_triangle)
        #cv2.imshow('img',img)
        #cv2.waitKey(0)
    with open('misc/mnid_to_triangle.pkl', 'wb') as f:
        pickle.dump(triangles3d, f)

def mnids_to_mappoints(mnids_to_triangles):
    """
    key: sorted((mnid1, mnid2, mnid3)) (from mnifs_to_triangles)
    values: (mp1,mp2,mp3)
    :param mnids_to_triangles:
    :return:
    """
    osmap_mnids_dict = {}
    for mappoint in my_osmap.map_points.mappoint:
        osmap_mnids_dict[mappoint.id] = mappoint
    mnid_triangle_to_mappoints = {}
    position_to_tuple = lambda x: (x.x, x.y, x.z)
    mappoint_to_pos_tuple = lambda x: position_to_tuple(x.position)
    for mnid1, mnid2, mnid3 in mnids_to_triangles:
        mappointtuple1 = mappoint_to_pos_tuple(osmap_mnids_dict[mnid1])
        mappointtuple2 = mappoint_to_pos_tuple(osmap_mnids_dict[mnid2])
        mappointtuple3 = mappoint_to_pos_tuple(osmap_mnids_dict[mnid3])
        mnid_triangle_to_mappoints[mnid1,mnid2,mnid3] = (mappointtuple1, mappointtuple2, mappointtuple3)
    return mnid_triangle_to_mappoints

def _sort_od_by_key(od):
    new_od = collections.OrderedDict(sorted(od.items(), key=lambda x: x[0]))
    new_od_index = list(new_od.keys())
    return new_od_index, new_od


class WavefrontObjWriter:
    def __init__(self, filename):
        self.filename = filename
        self.image_size = (1000,1000)
        self.texture_image = np.zeros(self.image_size+(3,), dtype=np.uint8) #@TODO datattype
        self.lines = []
        self.ti_points = collections.OrderedDict()
        self.textures_points = collections.OrderedDict()
        self.image_space_mask = np.array(np.zeros(self.image_size))
        self.stringify_point = "v {:.6f} {:.6f} {:.6f}".format
        self.stringify_texture_point = "vt {:.6f} {:.6f}".format
        self.points_string = io.StringIO()
        self.mappoints = collections.OrderedDict()
        self.mappoints_index  = None
        self.fourthpoints = collections.OrderedDict()
        self.last_texture_right_upper_corner = 0,0
        self.texture_points_string=io.StringIO()
        self.planes_string = io.StringIO()

    def add_point(self, mnid, mp):
        if self.points.get(mnid) is None:
            self.points[mnid] = mp
        else:
            raise ValueError

    def resize_image(self):
        #@TODO
        pass

    def reindex_tex_points(self):
        #@TOO
        pass

    def increase_image(self):
        self.resize_image()
        self.reindex_tex_points()

    def _triangle_points_to_texture_corrds(self, triangle_points, texture_base):
        xb, yb = texture_base
        return [(x+xb,y+yb) for (x,y) in triangle_points]

    def _texture_image_coords_to_uv(self, ti_coords):
        x,y = ti_coords
        u = x/self.image_size[0]
        v = (self.image_size[1]-y)/self.image_size[1]
        return u,v

    def _ti_triangle_to_uv(self, triangle):
        return [self._texture_image_coords_to_uv((x,y)) for x,y in triangle]

    def _find_new_line(self, texture_square):
        # @TODO double check this indeces are ok
        zero_indeces = np.where(self.image_space_mask[:,0]==0)
        # @TODO if zero indeces is empty this will not work (no new lines left)
        first_free_line = zero_indeces[0][0]
        return 0, first_free_line

    def find_free_space(self, texture_square):
        a,b = texture_square.shape[:2]
        # actually, not the last texture indeces, but th
        x_l,y_l = self.last_texture_right_upper_corner
        width_is_ok = x_l+1+a< self.image_size[1]
        height_is_ok = y_l+a < self.image_size[0]
        if  width_is_ok and height_is_ok:
            return x_l+1, y_l, a,b
        elif not width_is_ok and height_is_ok:
            return self._find_new_line(texture_square) + (a,b)
        elif not width_is_ok and not height_is_ok:
            self.increase_image() #@TODO this is not implemented
            raise ValueError("Not enough image space")

    def add_texture_to_image(self, texture_square):
        x,y, w,h = self.find_free_space(texture_square)#@TODO check if arguments order is correct
        self.texture_image[y:y+h, x:x+w] = texture_square
        self.image_space_mask[y:y+h, x:x+w] = 1
        self.last_texture_right_upper_corner = x+w,y
        return x,y,w,h

    def add_points_dict(self, mptriangledict):
        # K: sorted(mnid1, mnid2, mnid3), V: (p1,p2,p3)
        self.map_triangle_dict = mptriangledict
        for mnid_tuple, points in self.map_triangle_dict.items():
            for mnid, point in zip(mnid_tuple, points):
                if self.mappoints.get(mnid) == None:
                    self.mappoints[mnid] = point
        self._sort_mappoints()


    def _sort_mappoints(self):
        self.mappoints_index, self.mappoints = _sort_od_by_key(self.mappoints)
        self.fourthpoints_index, self.fourthpoints = _sort_od_by_key(self.fourthpoints)

    def add_texture(self, mnid_tuple_sorted, texture_square, triangle_points):
        assert texture_square.shape[0]==texture_square.shape[1], "It is not a square!"
        self.textures_points[mnid_tuple_sorted] = (texture_square, triangle_points)

    def save_texture(self):
        texture_points = collections.OrderedDict(sorted(self.textures_points.items(), key=lambda x:-x[1][0].shape[0]))
        for mnid_tuple_sorted, (texture_square, triangle_points)  in  texture_points.items():
            x,y,w,h = self.add_texture_to_image(texture_square)
            texture_image_triangle_points = self._triangle_points_to_texture_corrds(triangle_points, texture_base=(x,y))
            ti_triangle_uv = self._ti_triangle_to_uv(texture_image_triangle_points)
            self.ti_points[mnid_tuple_sorted] = ti_triangle_uv

    def _save_points(self):
        for mnid, point in self.mappoints.items():
            self.points_string.write(self.stringify_point(*point))
            self.points_string.write("\n")
        for fakemnid, fourthpoint in self.fourthpoints.items():
            self.points_string.write(self.stringify_point(*fourthpoint))
            self.points_string.write("\n")


    def _2D_distance(self, point_a, point_b):
        #just euclidean distance
        return np.linalg.norm(np.array(point_a)-np.array(point_b))

    def _find_longest_side(self, triangle_points):
        p1, p2, p3 = triangle_points
        sides = [(0,1), (1,2), (2,1)]
        sides_length = list(map(lambda point_index:self._2D_distance(triangle_points[point_index[0]], triangle_points[point_index[1]]), sides))
        index_longest = np.argmax(sides_length)
        return sides[index_longest]

    def _create_fourth_point(self, map_triangle, ti_triangle_uv):
        index_point_a, index_point_b = self._find_longest_side(ti_triangle_uv)
        map_equidistant_point = np.mean([map_triangle[index_point_a], map_triangle[index_point_b]], axis=0)
        texture_equidistant_point = np.mean( [ti_triangle_uv[index_point_a], ti_triangle_uv[index_point_b]],axis=0)
        return (index_point_a, index_point_b), map_equidistant_point, texture_equidistant_point

    def _get_mnid_obj_indeces(self, mnidlist):
        obj_ind_mps = list(map(lambda x: self.mappoints_index.index(x)+1, mnidlist))
        offset = len(self.mappoints_index)
        print(self.fourthpoints_index[0])
        fourth_index = self.fourthpoints_index.index(mnidlist) + offset + 1
        return obj_ind_mps + [fourth_index]

    def _save_texture_points_and_vertices(self):
        texture_point_string_line_count = 1
        for mnid_tuple, ti_triangle_uv in self.ti_points.items():
            assert len(ti_triangle_uv)==4
            plane_texture_point_obj_indeces = []
            for point in ti_triangle_uv:
                self.texture_points_string.write(self.stringify_texture_point(*point))
                self.texture_points_string.write("\n")
                plane_texture_point_obj_indeces.append(texture_point_string_line_count)
                texture_point_string_line_count += 1
            mnid1, mnid2, mnid3 = mnid_tuple
            #f v/vt v/vt v/vt v/vt
            stringify_plane = "f {mp[0]}/{tp[0]} {mp[1]}/{tp[1]} {mp[2]}/{tp[2]} {mp[3]}/{tp[3]}".format
            mappoints =  self._get_mnid_obj_indeces(mnid_tuple)
            self.planes_string.write(stringify_plane(mp=mappoints, tp=plane_texture_point_obj_indeces))
            self.planes_string.write("\n")


    def save_points_and_vertices(self):
        self._save_points()
        self._save_texture_points_and_vertices()

    def generate_fourth_points(self):
        self._sort_mappoints()
        for mnid_tuple, ti_triangle_uv in self.ti_points.items():
            if self.fourthpoints.get(mnid_tuple) is None:
                (mnid1, mnid2, mnid3) = mnid_tuple
                map_triangle = self.map_triangle_dict[mnid_tuple]
                mp1,mp2,mp3 = map_triangle
                mean_points_indeces, mp4, ti_uv_p4 = self._create_fourth_point(map_triangle, ti_triangle_uv)
                self.fourthpoints[mnid_tuple] = mp4
                self.ti_points[mnid_tuple] = ti_triangle_uv + [ti_uv_p4,]


    def save(self):
        self.save_texture()
        self.generate_fourth_points()
        self._sort_mappoints()
        self.save_points_and_vertices()
        cv2.imwrite(self.filename+".bmp", self.texture_image)
        with open(self.filename+'.obj', 'w') as f:
            f.write(self.points_string.getvalue())
            f.write(self.texture_points_string.getvalue())
            f.write(self.planes_string.getvalue())
            f.write("usemtl firstgen.mtl")
        with open(self.filename+'points.obj', 'w') as f:
            f.write(self.points_string.getvalue())




if __name__=='__main__':
    calibration_data_path = '/old_files/calib-wide.json'
    my_osmap= OsmapData()
    map_path = '/22_for_recoproc_2D.yaml'
    map_path = pathlib.Path(map_path)
    my_osmap.from_map_path(map_path.parent, map_path.stem)
    mtx, distCoeff = read_calibration(calibration_data_path)
    data_path = pathlib.Path('/home/mwm/Desktop/datadumps/01-07-19-drive-v1_22')
    assoc_path = '/proc2_assoc_im_kf.json'
    img_assoc_dict = read_assoc(assoc_path)
    #mnids_to_triangles(my_osmap, data_path, img_assoc_dict)
    with open('misc/mnid_to_triangle.pkl', 'rb') as f:
        mnids_to_triangles_dict= pickle.load(f)
    #mnid_triangle_to_mappoints = mnids_to_mappoints(mnids_to_triangles_dict)
    #with open('mnid_triangle_to_mappoints', 'wb') as f2:
    #    pickle.dump(mnid_triangle_to_mappoints, f2)
    with open('misc/mnid_triangle_to_mappoints', 'rb') as f2:
        mnid_triangle_to_mappoints = pickle.load(f2)
    writer = WavefrontObjWriter('firstgen')
    writer.add_points_dict(mnid_triangle_to_mappoints)
    for i, (mnidlist, value_dict_list) in enumerate(mnids_to_triangles_dict.items()):
        if i==950:
            break
        print(value_dict_list[-1])
        if len(value_dict_list)==0:
            print("not unique dict")
            print(value_dict_list)
            print()
        triangle_dict = value_dict_list[-1]
        texture_image = cv2.imread(str(data_path/triangle_dict['img']))
        triangle_cropped = get_cropped_roi_square(texture_image, triangle_dict['triangle'])
        #writer.add_texture(mnidlist, triangle_cropped, triangle_dict['triangle'])
    writer.save()


