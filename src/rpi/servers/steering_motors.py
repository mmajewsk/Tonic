import socket
import time
from steering import SteeringTranslatorRobot, MotorDriver
import json

"""
This script is as simple as possible, without the threads and whatnot.
It was created in that way to have minimal time constraint on the function of this code.
"""
host =''
port = 2203
server = socket.socket()
server.bind((host, port))
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()


start = time.time()

"""
You can rewrite this so it couldsupport your confoiguration of motors.
"""
steering_thread = MotorDriver()
while True:
	if time.time() - start > 600:
		break
	data = connection.recv(1024).decode()
	print(data)
	data = data.replace(" ","")
	steering_dict = json.load(data)
	steering_thread.go(steering_dict)

server.close()
