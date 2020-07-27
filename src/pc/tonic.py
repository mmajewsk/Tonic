import json
import yaml
from clients import ClientSink
from clients import video_client
from clients.steering_client import MotorClient
import cv2
import multiprocessing


class ServerSource:
    def __init__(self, *args, **kwargs):
        self.tasks = multiprocessing.JoinableQueue()
        self.results = multiprocessing.Queue()
        self.thread_video = video_client.MultiVideoClient(self.tasks, self.results, *args, **kwargs)

    def connect(self):
        self.thread_video.start()

    def get_data(self):
        self.tasks.put(True)
        img = None
        t = None
        while not self.results.empty():
            img, t = self.results.get()
            # print(img.shape)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img, t


class Tonic:
    def __init__(self, settings_file):
        settings = yaml.load(open(settings_file, 'rb'))
        server_ip = settings['server']['ip']
        video_port = settings['server']['video']['port']
        steering_port = settings['server']['steering']['port']
        self.video_client = ServerSource(server_adress=(server_ip, video_port), dt=0.001)
        self.steering_client = MotorClient(server_adress=(server_ip, steering_port), connect=True)
        self.steering_commands = None
        self.image = None
        self.timestamp = None
        self._prev_data = None, None


    def connect_video(self):
        self.video_client.connect()

    def steer_motors(self, data):
        self.steering_client.send(data)

    def image_now(self):
        data = self.video_client.get_data()
        if data[0] is None:
            return self._prev_data
        else:
            self._prev_data = data
            return self._prev_data
