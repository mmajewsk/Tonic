import socket
import time

def Main():
	host = '192.168.1.98'
	port = 2206

	mySocket = socket.socket()
	mySocket.connect((host, port))


	while True:

		mySocket.send('a'.encode())
		data = mySocket.recv(1024).decode()

		print('Received from server: ' + data)
		time.sleep(0.5)
	mySocket.close()


if __name__ == '__main__':
	Main()