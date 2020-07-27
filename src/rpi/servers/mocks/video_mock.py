#http://picamera.readthedocs.io/en/release-1.10/recipes2.html#rapid-capture-and-streaming

import socket
import os
import time
import cv2
from scipy import ndimage

if __name__ == "__main__":
    host ='0.0.0.0'
    port = 2201
    server = socket.socket()
    server.bind((host, port))
    server.listen(0)
    print("Starting server at {} port {}. Listening...".format(host,port))
    connection, adress = server.accept()
    binary_stream = connection.makefile('wb')
    images_path = "/home/mwm/repositories/Tonic/data_intake4/02_03_2020_hackerspace_v0.1"
    folder = images_path
    images = os.listdir(folder)
    images = filter(lambda x: ".jpg" in x, images)
    images_paths = sorted(images)
    #images = map(lambda x: (x.split("_")[1][:-4], x), images)
    images = map(lambda x: os.path.join(folder, x), images_paths)
    time.sleep(2)
    freq = 0.2
    path_to_time = lambda  x: float(x.split("_")[1][:-4])
    tprev = path_to_time(images_paths[0])
    for path, imgname in zip(images_paths,images):
        tn = path_to_time(path)
        dt = tn-tprev
        time.sleep(dt)
        tprev = tn
        img = cv2.imread(imgname)
        binary_stream.flush()
        success, encoded_image = cv2.imencode('.jpg', img)
        asbytes = encoded_image.tobytes()
        binary_stream.write(asbytes)

    binary_stream.close()
    server.close()