import argparse
from main_controller import QApplication,MainApp
import sys
from main_controller import Controller
from clients import QTVideoClient, QTSteeringClient

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Control the remote car')
	parser.add_argument('-v', dest='video', action='store_true',
						help='video on')
	parser.add_argument('-s', dest='steering', action='store_true',
						help='steering on')
	parser.add_argument('--dump_video', dest='dump_video', action='store_true', help='if folder is given, dump video')
	parser.add_argument('--dump_steering', dest='dump_steering', action='store_true',
						help='if folder is given, dump video')
	parser.add_argument('folder', metavar='folder', type=str, nargs=argparse.REMAINDER, default=None,
						help='where to store data dump')

	args = parser.parse_args()
	app = QApplication(sys.argv)
	server_ip = '192.168.1.239'
	video_client = None
	steering_client = None
	video_size = (320,240)
	if args.video:
		video_port = 2201
		video_client = QTVideoClient(server_adress=(server_ip, video_port), video_size=video_size)
	if args.steering:
		steering_port = 2203
		steering_client = QTSteeringClient(server_adress=(server_ip, steering_port))
	controller = Controller(video_client=video_client,
							intake_name=args.folder,
							steering_client=steering_client,
							dump_video=args.dump_video,
							dump_steering=args.dump_steering
							)
	win = MainApp(controller)
	win.show()
	sys.exit(app.exec_())
