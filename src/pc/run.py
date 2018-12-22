import argparse
from views import QApplication,MainApp, MapWindow
import sys
from controllers import Controller
from clients import QTVideoClient, QTSteeringClient, QTImuClient, ClientSink, QtSlamClient, QTOdoClient
from controllers import MapController
import yaml


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('--settings', dest='settings_file', type=str, default=None, help='if folder is given, dump video')
	parser.add_argument('-v', dest='video', action='store_true',
						help='video on')
	parser.add_argument('-s', dest='steering', action='store_true',
						help='steering on')
	parser.add_argument('-i', dest='imu', action='store_true',
						help='imu on')
	parser.add_argument('-o', dest='odo', action='store_true',
						help='odometry on')
	parser.add_argument('--dump_video', dest='dump_video', action='store_true', help='if folder is given, dump video')
	parser.add_argument('--dump_steering', dest='dump_steering', action='store_true', default=False,
						help='if folder is given, dump video')
	parser.add_argument('--dump_imu', dest='dump_imu', action='store_true',
						help='if folder is given, dump raw imu')
	parser.add_argument('--dump_odo', dest='dump_odo', action='store_true',
						help='if folder is given, dump raw odometry')
	parser.add_argument('folder', metavar='folder', type=str, nargs=argparse.REMAINDER, default=None,
						help='where to store data dump')

	args = parser.parse_args()
	settings_path = 'settings.yaml'
	if args.settings_file is not None:
		settings_path = args.settings_file
	settings = yaml.load(open(settings_path, 'rb'))
	app = QApplication(sys.argv)
	server_ip = settings['server']['ip']
	video_client = None
	steering_client = None
	imu_client = None
	slam_client=None
	odo_client=None
	slam_ip = settings['server']['slam']['ip']
	slam_port = settings['server']['slam']['port']
	video_size = settings['hardware']['camera']['image']['shape'][:2]
	if args.video:
		video_port = settings['server']['video']['port']
		video_client = QTVideoClient(server_adress=(server_ip, video_port), video_size=video_size)
	if args.steering:
		steering_port = settings['server']['steering']['port']
		steering_client = QTSteeringClient(server_adress=(server_ip, steering_port))
	if args.imu:
		imu_port = settings['server']['imu']['port']
		imu_client = QTImuClient(server_adress=(server_ip, imu_port))
		slam_client = QtSlamClient(server_adress=(slam_ip, slam_port))
	if args.odo:
		odo_port = settings['server']['odo']['port']
		odo_client = QTOdoClient(server_adress=(server_ip, odo_port))

	client_sink = ClientSink(video_client=video_client,
							 steering_client=steering_client,
							 imu_client=imu_client,
							 slam_client=slam_client,
							 odo_client=odo_client)
	controller = Controller(client_sink=client_sink,
							intake_name=args.folder,
							dump_video=args.dump_video,
							dump_steering=args.dump_steering,
							dump_odo=args.dump_odo
							)
	other_windows=[]
	if args.imu:
		map_controller = MapController(client_sink,dump_imu=args.dump_imu, intake_name=args.folder)
		win2 = MapWindow(map_controller)
		other_windows.append(win2)
	win = MainApp(controller, other_windows)
	win.show()
	for window in other_windows:
		window.show()
	sys.exit(app.exec_())
