# Software Guide

So in order to make the robot work, you need to setup everything on raspberry ([car setup](#car-setup)) and on your pc ([remote control](#remote-control)).

## Steps to run in data taking mode

There is some set up required, before you can run this:

0. Set up the [RPI0](#car-setup)
1. (callibrate the IMU, but only if you need it)
2. Set up the `settings.yml` correctly
3. Set up desired services on the RPI0(Video, Steering, Imu, Odometry).
4. [Set up remote control](#remote-control-setup) and run it.

## (Deprecated) Steps to run in live orb_slam mode

There is some set up required, before you can run this:

0. Set up the [RPI0](#car-setup) and [SLAM docker](https://github.com/mmajewsk/orb_slam_py2_docker)
1. callibrate the camera
2. callibrate the IMU
3. Set up the `settings.yml` correctly
4. Set up desired services on the RPI0(Video, Steering, Imu, Odometry), or on laptop (SLAM).
5. Run Tonic 


# Remote Control

## Prerequisistes

**Python** - Of course, Tonic is written almost entirely in python, so you will be needing python 3.6 at least. I highly recommend using [Anaconda](https://www.anaconda.com/download/)

**OpenCV** - For some scripts it will be necessesary to use OpenCV. No way around it. 
If you are using anaconda you can simply do :

```
conda install -c menpo opencv
```
**Python Dependencies**

You are using python, so just do:

```
pip install -r requirements.txt
```

**Warning** I did not test different configrations, hit the issues in github if something is not working for you.


# Remote control setup

You need to follow these steps:

### 1. Seting up RPI0 and SLAM
For guide for setting up RPI0 look [here](#device-setup).
How to set up SLAM docker see [here](https://github.com/mmajewsk/orb_slam_py2_docker).

### 2. Configuring settings.yml

In the `pc` folder there is `settings.yml` file. Lets take a look:

```
info:
  settings: v1
  car:
    build: mark2
    name: car1
hardware:
  camera:
    calibration_file:
      path: camera_calibration/calib.json
      type: json
    image:
      shape: [320, 240, 3]
server:
  ip: '192.168.1.98'

  video:
    port: 2201
    command: "python -u video_streaming.py"
  steering:
    port: 2203
    command: "python3 -u steering_server.py"
  imu:
    port: 2204
    command: "python -u imu_server.py"
  odo:
    port: 2206
    command: "python3 -u odometry.py"
  slam:
    ip: '127.0.0.1'
    port: 2207
  master:
    port: 2205
```

We can divide it into three parts:

`info` - just some informations, not really important.

`hardware` - stores information about desired images shape as well as path to json containing calibration.

`server` - stores the configuration of services. the `ip` is the ip of the RPI0, fill it in accordingly.
Also fill in the `ip` in `slam`, if you are not running it on the same machine as Tonic.


### 3. Running Tonic

```
python run.py -v -s
```

This should run the Tonic with connected Video feed and active steering.
The steering (WASD keys only!) is only active when you have clicked into the window with the feed.
You can run Tonic with any number of options specified in the help menu.
Altough, **to run SLAM you have to run it with Imu** (`-i`).

To collect the all data from all sensors, you should run:

```
python run.py -s -v -i -o --dump_video --dump_steering --dump_imu --dump_odo /path/to/folder/to/dump/data/to
```

Each of the options is described in help `python run.py -h`.
**Remember to change the folder if you want to take new data, because it will defaultly overwrite existing data**

# Car Setup

This section will guide throug the usage of the `car` folder.
The code was used on Raspberry Pi Zero with WIFI.
It was not tested on any other device.

## How to use this

The recommended workflow is to open as many ssh connections from your machine to the RPI as needed and in each ssh run one of the services.
This is also why some of the requirements are mutually exclusive (python 2 and 3). But you should have both installed, and just run the separately.
Yes, this is not nice, but unifying everything so it would work as reliably is on the todo list ;)  


## Prerequistes

I am assuming that your car is already built. If not you can use [the hardware guide](#hardware_guide.md).
After you will set up the car, you need to be connect it to the same network as the device that you will be running Tonic on.
There is enough guides on how to connect the RPI to the wifi already so go and find one.
Remember to put the Raspberrys IP into the [settings](#2.-configuring-settings)

As stated previously you can skip the IMU and odometry steps, and use only steering and video.

**Video** - This service requires **Python 2** [picamera](https://picamera.readthedocs.io), but it should already be in your raspberry.
Remember to enable the camera in the RPI settings!

**Steering** - Nothing more than [RPI GPIO](https://pypi.org/project/RPi.GPIO/) and **python 3**

**Odometry** - Nothing more than [RPI GPIO](https://pypi.org/project/RPi.GPIO/) and **python 3**

**IMU** - The imu services uses external IMU driver, [minimu9-ahrs](https://github.com/DavidEGrayson/minimu9-ahrs) by DavidEGrayson. This one might be tough, but the guide on the drivers repo got me through anyway, be patient, make sure that you have nabled the correct settings, and everything is well soldered and connected. 
the guide is [here](https://github.com/DavidEGrayson/minimu9-ahrs#getting-started). Godspeed!

Internally this service opens `subprocess.Popen` to call miminu9-ahrs (yeah, i know, thats not the best solution, but I tried wrapping it in python and it took too much time).
**Make sure that minimu9-ahrs is working and is accesible for that script, and that it is callibrated!**


## Running

**Video**:

```
python video_streaming.py
```

And thats it.
If the connection is interupted, you might need to restart the service.

**Steering**


```
python3 steering_server.py
```

If your steering does not match with your hardware, you can easilly manipulate the code to get the desired output.
If the connection is interupted, you might need to restart the service.

**IMU**

```
python imu_server.py
```

Additionaly, if you will stop connection with the Tonic/pc, you dont need to reset this service.

**Odometry**


```
python3 odometry.py
```

## Unifying the service (not fully supported)

There was an attempt to unify every service, so it would not need 4 windows to be managed.
You can see the code in the file `master_server.py`.
