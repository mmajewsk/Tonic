import time
import datetime

while True:
	time.sleep(0.1)
	print("Ok[{}]".format(datetime.datetime.now()))
	for i in range(2):
		time.sleep(1)
		print("Ok[{}]".format(datetime.datetime.now()))
