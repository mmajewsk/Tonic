#http://picamera.readthedocs.io/en/release-1.10/recipes2.html#rapid-capture-and-streaming

import io
import socket
import struct
import time

import picamera

host =''
port = 2201
server = socket.socket()
server.bind((host, port))
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()
binary_stream = connection.makefile('rb')



with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 10
    camera.color_effects = (128,128)
    time.sleep(2)
    start = time.time()
    stream = io.BytesIO()
    for foo in camera.capture_continuous(stream, 'jpeg',
                                         use_video_port=True):
        binary_stream.flush()
        stream.seek(0)
        binary_stream.write(stream.read())
        if time.time() - start > 60:
            break
        stream.seek(0)
        stream.truncate()


binary_stream.close()
server.close()