from abc import ABCMeta, abstractmethod
import RPi.GPIO as GPIO
import time
import multiprocessing
import functools

class Steering(metaclass=ABCMeta):

	@abstractmethod
	def wheel_right(self, val):
		pass


	@abstractmethod
	def wheel_left(self, val):
		pass

	@abstractmethod
	def wheel_straight(self, val):
		pass

	@abstractmethod
	def stop_car(self, val):
		pass

	@abstractmethod
	def forward(self, val):
		pass

	@abstractmethod
	def backward(self, val):
		pass

class Motor:
	"""
	This class conttains logic for GPIO motor.
	"""
	def __init__(self, enabler_pin, plus_pin, minus_pin, velocity=0, high=100, frequency=100):
		self.enabler_pin = enabler_pin
		self.default_velocity = velocity
		self.minus_pin = minus_pin
		self.plus_pin = plus_pin
		GPIO.setup(enabler_pin, GPIO.OUT)
		GPIO.setup(minus_pin, GPIO.OUT)
		GPIO.setup(plus_pin, GPIO.OUT)
		self.enabler = GPIO.PWM(enabler_pin, frequency)
		self.LOW = 0
		self.HIGH = high
		self.enabler.start(0)
		self.last_val=0


	def set_values(self, val, p_val, m_val):
		val = val if val is not None else self.default_velocity
		self.enabler.ChangeDutyCycle(val)
		GPIO.output(self.plus_pin,p_val)
		GPIO.output(self.minus_pin, m_val)

	def __del__(self):
		self.enabler.stop()


class SteeringDriverRobot(Steering):
	"""
	This class implements the functions of the movement for the car.
	You can create a new one like this so it would cover your configuration.
	"""
	def __init__(self, **kwargs):
		GPIO.setmode(GPIO.BCM)
		self.motor_a = Motor(enabler_pin=0, plus_pin=5, minus_pin=6, **kwargs['left_motor'])
		self.motor_b = Motor(enabler_pin=26, plus_pin=19, minus_pin=13, **kwargs['right_motor'])

	def wheel_right(self, val=None):
		pass

	def wheel_left(self, val=None):
		pass

	def forward(self, val=None):
		self.motor_a.set_values(val, self.motor_a.HIGH, self.motor_a.LOW)
		self.motor_b.set_values(val, self.motor_b.HIGH, self.motor_b.LOW)

	def backward(self, val=None):
		self.motor_a.set_values(val, self.motor_a.LOW, self.motor_a.HIGH)
		self.motor_b.set_values(val, self.motor_b.LOW, self.motor_b.HIGH)

	def stop_car(self, val=None):
		self.motor_a.set_values(0, self.motor_a.HIGH, self.motor_a.HIGH)
		self.motor_b.set_values(0, self.motor_b.HIGH, self.motor_b.HIGH)

	def wheel_straight(self, val=None):
		pass

	def forward_left(self, val=None):
		self.motor_a.set_values(10, self.motor_a.HIGH, self.motor_a.LOW)
		self.motor_b.set_values(val, self.motor_b.HIGH, self.motor_b.LOW)

	def backward_left(self, val=None):
		self.motor_a.set_values(10, self.motor_a.LOW, self.motor_a.HIGH)
		self.motor_b.set_values(val, self.motor_b.LOW, self.motor_b.HIGH)

	def forward_right(self, val=None):
		self.motor_a.set_values(val, self.motor_a.HIGH, self.motor_a.LOW)
		self.motor_b.set_values(10, self.motor_b.HIGH, self.motor_b.LOW)

	def backward_right(self, val=None):
		self.motor_a.set_values(val, self.motor_a.LOW, self.motor_a.HIGH)
		self.motor_b.set_values(10, self.motor_b.LOW, self.motor_b.HIGH)
	def __del__(self):
		GPIO.cleanup()


class SteeringDriverCar(Steering):
	def __init__(self, **kwargs):
		GPIO.setmode(GPIO.BCM)
		self.motor_a = Motor(enabler_pin=22, plus_pin=17, minus_pin=27, **kwargs['thrust'])
		self.motor_b = Motor(enabler_pin=24, plus_pin=4, minus_pin=23, **kwargs['steer'])

	def wheel_right(self, val=None):
		self.motor_b.set_values(val, self.motor_b.LOW, self.motor_b.HIGH)

	def wheel_left(self, val=None):
		self.motor_b.set_values(val, self.motor_b.HIGH, self.motor_b.LOW)

	def forward(self, val=None):
		self.motor_a.set_values(val, self.motor_a.HIGH, self.motor_a.LOW)

	def backward(self, val=None):
		self.motor_a.set_values(val, self.motor_a.LOW, self.motor_a.HIGH)

	def stop_car(self, val=None):
		self.motor_a.set_values(30, self.motor_a.HIGH, self.motor_a.HIGH)

	def wheel_straight(self, val=None):
		self.motor_b.set_values(val, self.motor_b.LOW, self.motor_b.LOW)

	def __del__(self):
		GPIO.cleanup()


class SteeringTranslator(Steering):
	def __init__(self, time_delay=0.4, **kwargs):
		self.time_delay = time_delay
		self.translator={
			'go_straight':[self.wheel_straight,self.forward],
			'go_backward':[self.wheel_straight,self.backward],
			'stop':[self.wheel_straight,self.stop_car],
			'forward_left':[self.forward, self.wheel_left],
			'forward_right': [self.forward, self.wheel_right],
			'backward_left': [self.backward, self.wheel_left],
			'backward_right': [self.backward, self.wheel_right],
			'left': [self.wheel_left],
			'right': [self.wheel_right],
		}
		self.command = ''
		self.old_signal = 'stop'

	def work(self, new_signal):
		if self.old_signal != new_signal:
			for f in self.translator[new_signal]:
				f()
			self.old_signal=new_signal
		time.sleep(self.time_delay)


	def run(self):
		signal = self.command_to_signal(self.command)
		print(signal)
		self.work(signal)


	def command_to_signal(self, command):
		if command.isspace() or not command:
			return 'stop'
		else:
			if 'w' in command and 'a' in command:
				return 'forward_left'
			elif 'w' in command and 'd' in command:
				return 'forward_right'
			elif 's' in command and 'a' in command:
				return 'backward_left'
			elif 's' in command and 'd' in command:
				return 'backward_right'
			elif 'd' in command:
				return 'right'
			elif 'a' in command:
				return 'left'
			elif 'w' in command:
				return 'go_straight'
			elif 's' in command:
				return 'go_backward'
			else:
				return 'stop'

class SteeringTranslatorCar(SteeringTranslator, SteeringDriverCar):
	def __init__(self, **kwargs):
		SteeringDriverCar.__init__(self, **kwargs)
		SteeringTranslator.__init__(self, **kwargs)

class SteeringTranslatorRobot(SteeringTranslator, SteeringDriverRobot):
	"""
	This class translates the commands to the functions of steering.
	"""
	def __init__(self, **kwargs):
		SteeringDriverRobot.__init__(self, **kwargs)
		SteeringTranslator.__init__(self, **kwargs)
		self.translator['go_straight'] = [self.forward]
		self.translator['go_backward'] = [self.backward]
		self.translator['stop'] = [self.stop_car]
		self.translator['forward_left'] = [self.forward_left]
		self.translator['forward_right'] = [self.forward_right]
		self.translator['backward_left'] = [self.backward_left]
		self.translator['backward_right'] = [self.backward_right]


def keys_to_command(keys):
		w,s,a,d = 87,83,68,65
		keytab = map(lambda x: keys[x], (w,s,a,d))
		command = sum(1<<i for i, b in enumerate(keytab) if b)
		return command

if __name__=='__main__':
	GPIO.setmode(GPIO.BCM)
	left_motor = dict(velocity=20, frequency=50, high=100)
	right_motor = dict(velocity=20, frequency=50, high=100)
	s = SteeringTranslatorRobot(left_motor=left_motor, right_motor=right_motor, time_delay=0.05)
	#s.signal = 'w'
	#s.run()
	s.stop_car()
	s.forward()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.stop_car()
	s.forward()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.stop_car()
	s.backward()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)


	s.stop_car()
	s.forward_left()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.stop_car()
	s.backward_left()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.stop_car()
	s.forward_right()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.stop_car()
	s.backward_right()
	time.sleep(0.2)
	s.stop_car()
	time.sleep(1)

	s.signal = ''
	#s.run()
	del s
	time.sleep(0.4)
