from clients import ImuWorker
import numpy as np
def data_to_array(data):
	return np.reshape(np.array(data),(3,3))


acc_conv = 0.244 #FS=8
gyr_conv = 70


if __name__=='__main__':
	server_adress = ('192.168.1.239', 2204)
	w = ImuWorker(server_adress=server_adress,dt=0.5)
	l = []
	for i in range(15):
		data=w.read()
		print(data)
		l.append(data_to_array(data))
		print("----")
	m = np.array(l)
	mean = m.mean(0)
	while True:
		data = w.read()
		data = data_to_array(data)
		print(data-mean)