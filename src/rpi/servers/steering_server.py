import socket
import time
from steering import SteeringTranslatorRobot

host =''
port = 2203
server = socket.socket()
server.bind((host, port))
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()


start = time.time()

left_motor = dict(velocity=20, frequency=50, high=100)
right_motor = dict(velocity=20, frequency=50, high=100)
steering_thread = SteeringTranslatorRobot(left_motor=left_motor, right_motor=right_motor, time_delay=0.05)

while True:
	if time.time() - start > 600:
		break
	data = connection.recv(1024).decode()
	print(data)
	data = data.replace(" ","")
	steering_thread.command = data
	steering_thread.run()

server.close()
