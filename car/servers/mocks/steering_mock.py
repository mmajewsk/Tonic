import socket
import time
import logging
logging.basicConfig(
    format='[%(asctime)s][%(funcName)s]%(message)s',
    datefmt='%I:%M:%S %p',
    level=logging.INFO
)

"""
This script is as simple as possible, without the threads and whatnot.
It was created in that way to have minimal time constraint on the function of this code.
"""
host =''
port = 2203
server = socket.socket()
server.bind((host, port))
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.listen(0)
print("Starting server at {} port {}. Listening...".format(host,port))
connection, adress = server.accept()


start = time.time()

"""
You can rewrite this so it couldsupport your confoiguration of motors.
"""

while True:
    if time.time() - start > 600:
        break
    data = connection.recv(1024).decode()
    logging.info(data)
    data = data.replace(" ","")

server.close()
