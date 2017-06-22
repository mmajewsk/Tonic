import argparse
from views import QApplication,MainApp, MapWindow
import sys
from controllers import Controller
from clients import QTVideoClient, QTSteeringClient, QTImuClient, ClientSink
from controllers import MapController


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('-v', dest='video', action='store_true',
						help='video on')
	parser.add_argument('-s', dest='steering', action='store_true',
						help='steering on')
	parser.add_argument('-i', dest='imu', action='store_true',
						help='imu on')
	parser.add_argument('--dump_video', dest='dump_video', action='store_true', help='if folder is given, dump video')
	parser.add_argument('--dump_steering', dest='dump_steering', action='store_true', default=False,
						help='if folder is given, dump video')
	parser.add_argument('--dump_imu', dest='dump_imu', action='store_true',
						help='if folder is given, dump raw imu')
	parser.add_argument('folder', metavar='folder', type=str, nargs=argparse.REMAINDER, default=None,
						help='where to store data dump')

	args = parser.parse_args()
	app = QApplication(sys.argv)
	server_ip = '192.168.1.239'
	video_client = None
	steering_client = None
	imu_client = None
	video_size = (320,240)
	if args.video:
		video_port = 2201
		video_client = QTVideoClient(server_adress=(server_ip, video_port), video_size=video_size)
	if args.steering:
		steering_port = 2203
		steering_client = QTSteeringClient(server_adress=(server_ip, steering_port))
	if args.imu:
		imu_port = 2204
		imu_client = QTImuClient(server_adress=(server_ip, imu_port))
	client_sink = ClientSink(video_client=video_client,
							 steering_client=steering_client,
							 imu_client=imu_client)
	controller = Controller(client_sink=client_sink,
							intake_name=args.folder,
							dump_video=args.dump_video,
							dump_steering=args.dump_steering
							)
	map_controller = MapController(client_sink,dump_imu=args.dump_imu, intake_name=args.folder)
	other_windows=[]
	if args.imu:
		win2 = MapWindow(map_controller)
		other_windows.append(win2)
	win = MainApp(controller, other_windows)
	win.show()
	for window in other_windows:
		window.show()
	sys.exit(app.exec_())
