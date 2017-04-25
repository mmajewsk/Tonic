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
	def __init__(self, enabler_pin, plus_pin, minus_pin, velocity=0, high=100, frequency=100):
		self.enabler_pin = enabler_pin
		self.default_velocity = velocity
		self.minus_pin = minus_pin
		self.plus_pin = plus_pin
		GPIO.setup(enabler_pin, GPIO.OUT)
		GPIO.setup(minus_pin, GPIO.OUT)
		GPIO.setup(plus_pin, GPIO.OUT)
		self.enabler = GPIO.PWM(enabler_pin, frequency)
		#self.minus = GPIO.PWM(minus_pin, frequency)
		#self.plus = GPIO.PWM(plus_pin, frequency)
		self.LOW = 0
		self.HIGH = high
		self.enabler.start(0)
		self.last_val=0


	def set_values(self, val, p_val, m_val):
		val = val if val is not None else self.default_velocity
		self.enabler.ChangeDutyCycle(val)
		#self.plus.start(p_val)
		#self.minus.start(m_val)
		#GPIO.output(self.enabler_pin, val)
		GPIO.output(self.plus_pin,p_val)
		GPIO.output(self.minus_pin, m_val)

	def __del__(self):
		self.enabler.stop()
		#self.plus.stop()
		#self.minus.stop()

		#GPIO.output(self.enabler_pin, self.LOW)
		GPIO.output(self.plus_pin, self.LOW)
		GPIO.output(self.minus_pin, self.LOW)


class SteeringDriver(Steering):
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
		self.motor_a.set_values(0, self.motor_a.LOW, self.motor_a.LOW)

	def wheel_straight(self, val=None):
		self.motor_b.set_values(val, self.motor_b.LOW, self.motor_b.LOW)

	def __del__(self):
		GPIO.cleanup()

class SteeringTranslator(SteeringDriver):#,multiprocessing.Process):
	def __init__(self, time_delay=0.4, **kwargs):
		super().__init__(**kwargs)
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

def keys_to_command(keys):
		w,s,a,d = 87,83,68,65
		keytab = map(lambda x: keys[x], (w,s,a,d))
		command = sum(1<<i for i, b in enumerate(keytab) if b)
		return command

if __name__=='__main__':
	s = SteeringTranslator()
	#s.signal = 'w'
	#s.run()
	s.stop_car()
	s.forward()
	time.sleep(0.4)
	s.signal = ''
	#s.run()
	del s
	time.sleep(0.4)