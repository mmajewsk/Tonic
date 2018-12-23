# Software Guide

## Prerequisites

### Python

Of course, Tonic is written almost entirely in python, so you will be needing python 3.6 at least.
I highly recommend using [Anaconda](https://www.anaconda.com/download/)

### OpenCV

For some scripts it will be necessesary to use OpenCV. No way around it. 
If you are using anaconda you can simply do :

```
conda install -c menpo opencv
```

###

## Dependencies

You are using python, so just do:

```
pip install -r requirements.txt
```

**Warning** I did not test different configrations, hit the issues in github if something is not working for you.

## Setting Up

There is some set up required, before you can run this:

0. Set up the [RPI0](https://github.com/mmajewsk/Tonic/blob/master/device_setup.md), and [SLAM docker](https://github.com/mmajewsk/orb_slam_py2_docker)
1. callibrate the camera
2. callibrate the IMU
3. Set up the `settings.yml` correctly
4. Set up desired services on the RPI0(Video, Steering, Imu, Odometry), or on laptop (SLAM).
5. Run Tonic 

### Seting up RPI0 and SLAM
For guide for setting up RPI0 look [here](https://github.com/mmajewsk/Tonic/blob/master/device_setup.md).
How to set up SLAM docker see [here](https://github.com/mmajewsk/orb_slam_py2_docker).

### Configuring settings.yml

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


### Setting up services
You can find the guide [here](https://github.com/mmajewsk/Tonic/blob/master/device_setup.md#setting-up-the-raspberry).

## Running Tonic

```
python run.py -v -s
```

This should run the Tonic with connected Video feed and active steering.
The steering is only active when you have clicked into the window with the feed.
You can run Tonic with any number of options specified in the help menu.
Altough, **to run SLAM you have to run it with Imu** (`-i`).

To collect the all data from all sensors, you should run:

```
python run.py -s -v -i -o --dump_video --dump_steering --dump_imu --dump_odo /path/to/folder/to/dump/data/to
```

Each of the options is described in help `python run.py -h`.
**Remember to change the folder if you want to take new data, because it will defaultly overwrite existing data**

### Turning the services by Tonic (not fully supported)

There was an attempt to simplify the process of turning everything on, you can see the code used to do that in the file `service_run.py`.
