# Device Setup

This file will guide throug the usage of the `rpi` folder.
The code was used on Raspberry Pi Zero with WIFI.
It was not tested on any other device.

## Setting up the raspberry

First of all, you need to e connected to the same network as the device that you will be running Tonic on.
There is enough guides on how to connect the RPI to the wifi already so go and find one.
Remember to put the Raspberrys IP into the [settings]()
If you will do that, you should build the device toghether, as it is inthe [hardware guide]()

## How to use this

The recommended workflow is to open as many ssh connections from your machine to the RPI as needed and in each ssh run one of the services.
Yes, this is not nice, but unifying everything so it would work as reliably and would be as easy to monitor is not trivial task.

## Video

### Requirements

This service requires **Python 2** [picamer](https://picamera.readthedocs.io), but it should already be in your raspberry.
Remember to enable the camera in the RPI settings!


### Running

So video server is very basic and simple.
You can run it by

```
python video_streaming.py
```

And thats it.
If the connection is interupted, you might need to restart the service.

## Steering

This service is well build and designed. If your steering does not match with your hardware, you can easilly manipulate the code to get the desired output.

### Requirements

Nothing more than [RPI GPIO](https://pypi.org/project/RPi.GPIO/) and **python 3**

### Running

Just run:

```
python3 steering_server.py
```

If the connection is interupted, you might need to restart the service.

## IMU

The imu services uses external IMU driver, [minimu9-ahrs](https://github.com/DavidEGrayson/minimu9-ahrs) by DavidEGrayson.

### Prerequisistes

This one might be tough, but the guide on the drivers repo got me through anyway, be patient, make sure that you have nabled the correct settings, and everything is well soldered and connected. 
the guide is [here](https://github.com/DavidEGrayson/minimu9-ahrs#getting-started). Godspeed!

Internally this service opens `subprocess.Popen` to call miminu9-ahrs (yeah, i know, thats not the best solution, but I tried wrapping it in python and it took too much time).
**Make sure that minimu9-ahrs is working and is accesible for that script, and that it is callibrated!!!!**

### Running

```
python imu_server.py
```

Additionaly, if you will stop connection with the Tonic/pc, you dont need to reset this service.

## Odometry

This service was the last that i have written. Its by far one of the most engineered one. The goal here was to make some unifying modules for all services, hence the `server_magement` module. 

### Prerequisites

Nothing more than [RPI GPIO](https://pypi.org/project/RPi.GPIO/) and **python 3**

### Running

```
python3 odometry.py
```

## Unifying the service (not fully supported)

There was an attempt to unify every service, so it would not need 4 windows to be managed.
You can see the code in the file `master_server.py`.

