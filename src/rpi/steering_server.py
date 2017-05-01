#http://picamera.readthedocs.io/en/release-1.10/recipes2.html#rapid-capture-and-streaming

import io
import socket
import struct
import time
from steering import SteeringTranslator
import picamera

from datetime import datetime

host =''
port = 2203
server = socket.socket()
server.bind((host, port))
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()


start = time.time()

steer = dict(velocity=40, frequency=50, high=100)
thrust = dict(velocity=15, frequency=50, high=100)
steering_thread = SteeringTranslator(steer=steer, thrust=thrust, time_delay=0.05)

while True:
	if time.time() - start > 60:
		break
	data = connection.recv(1024).decode()
	print(data)
	data = data.replace(" ","")
	steering_thread.command = data
	steering_thread.run()

server.close()