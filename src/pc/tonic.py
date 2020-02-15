import yaml
from clients import ClientSink, QTVideoClient, QTSteeringMotor

class Tonic:
    def __init__(self, settings_file):
        settings = yaml.load(open(settings_file, 'rb'))
        server_ip = settings['server']['ip']
        video_size = settings['hardware']['camera']['image']['shape'][:2]
        video_port = settings['server']['video']['port']
        steering_port = settings['server']['steering']['port']
        video_client = QTVideoClient(server_adress=(server_ip, video_port), video_size=video_size)
        steering_client = QTSteeringMotor(server_adress=(server_ip, steering_port))
        self.client_sink = ClientSink(
            video_client=video_client,
            steering_client=steering_client
        )
        self.steering_commands = None

    def connect_steering(self):
        self.client_sink.start_steering(self)

    def add_image(self, frame):
        self.image = frame[0]
        self.timestamp = frame[1]

    def connect_video(self):
        """Initialize camera.
        """
        self.client_sink.connect_to_video(self.add_image)

    def steer_motors(self, data):
        self.steering_commands = data

    def image_now(self):
        while True:
            yield self.image, self.timestamp