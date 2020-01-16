![](https://imgur.com/uKuppcF.jpg)

# Autonomous Intelligent Car 
(Or just a Roomba, that does not suck ;) )

I present to You, the autonomous car, (almost) entirely written in Python.

**Contents:**

1. [Old Version](#old-version)
2. [New Version](#the-third-version)
3. [Hardware Guide](#hardware-guide)
4. [List of components](#list-of-components)
5. [Connecting the wires](#connecting-the-wires)
6. [Software Guide](#software-guide)
7. [Device setup](#device-setup)

# Old version

Video

[![second version (video)](https://img.youtube.com/vi/XM7lNRdp8ow/0.jpg)](https://www.youtube.com/watch?v=XM7lNRdp8ow)

## How does it work:

The software is communicating with Raspberry Pi via WiFi network, using sockets. Sensors, camera, and steering - each one is implemented
as a separate service on socket.
You can steer it with keyboard on PC, and have an live feed from camera.
All of the sensors, stearing and video can be dumped to files on PC.
All written in Python.

## The Goal
To implement a SLAM capability, that would enable the car to map the environemnt and navigate.

## Achievements of the first version.
  - Working camera feeed
  - Working steering system
  - Working IMU
  - Partian SLAM implemented
  - Using only the feed from camera, it can map the environment to "birds eye view"
  
  **Attention! This is cool!** ORB-slam working on the camera feed (video):
  
  [![Second version (video)](https://img.youtube.com/vi/XR-vKycwOm8/0.jpg)](https://www.youtube.com/watch?v=XR-vKycwOm8)
  
  **C A R E F U L! This is cool as well** 2D map from the video feed (video):
  
  [![Second version (video)](https://img.youtube.com/vi/Wd5jEd4hx6U/0.jpg)](https://www.youtube.com/watch?v=Wd5jEd4hx6U)
  
  [![3D reconstruction](https://img.youtube.com/vi/oRmxJyJHEtU/0.jpg)](https://www.youtube.com/watch?v=oRmxJyJHEtU)
  
  ![wwwwowww](https://media.giphy.com/media/OK27wINdQS5YQ/giphy.gif)

  
# The third version


![Third version, less spectacular](https://lh3.googleusercontent.com/IuCSr21Cb3tGpGMnIhsa7TThIg2WQow34TMnW2t3mI2jwENIGsg7YI2H-PUxN7tL1rPp5GF8OytFAX5TnJt4F91LoR5jvWLSZfbNOt-bqljZWx_-JIScLlvS8kxXzLI2Gl5FW_V-4n8G2psZsI2k11mGIHGzmENbIgd1157-BmnFWVcFHjPWYQiKbv_6vLWFJmYBeK4ICtQrbBSLLpSVLlJoUGQLrAGPiltxqREM2potxoTvzC1uk4joj2DezeMMhbXHsouxb-veooV5JQUoD2KNKSOuwWNTJy7wCSLCP7bKnq5WOK7klRYwIx4nhzVjPGsIMBqVnM15oarJQVdWVM-cJr0SAhowkN2LHgan0iTv56c5mLPj6WO0Rhsg6H6f9YSMKIieSHfKuPdo44S4-Foa54bNrneKJ7gbCveb5hEwNuFyEbp-QbFYruM3aJ-113DGR29Fb0GkyQczrmi7Nr5teJlE_0DOf8V22BuAhgfWqvsuHxakuo4GFyOPKOLtgclmE0enZLRjDV5R5vBZ2DtZIwuDwUgBv_kpZTwIVqcrZFJ-hiMxG4rVD-6fxH_p4hclV3qyV7BUZyOnHyXiyLOh1Liglgfismk5ZBtzackYbYXSuWPvHRvD7tSXbFObZ4aH4Z-vawgQeaY8QT4tLKXImYnEGanmDq3ttEevNlh40Gf4aWk5v7IVdFno2qg9EiqIc1KLZSdT38J3fMY=w1433-h806-no)

Third version was created because of the problems with the steering (cheap remote controled cars have low quality gears inside). 
Also, in the previous version, any manipulation of the circuits, was difficult because of the casing. 
Also it was difficult to get good odometry readout. 

So i changed the body of the car as well as the wheels. 
Looks a bit worse, but is waaaaay more effective ;]

**Third version has working odometry system**

## What can be improved:

![](https://rlv.zcache.com/uncle_sam_i_want_you_poster-rad708dab64b04b6e8f41bb6beece2194_q1kv_8byvr_540.jpg)

If you would like to help, or have questions regarding the project, see ![here](https://github.com/mmajewsk/Tonic/issues).


# Hardware Guide

## List of components

- [Raspberry Pi Zero W](https://www.amazon.com/Raspberry-Pi-Zero-Wireless-model/dp/B06XFZC3BX) 
- [Pololu MinIMU-9 v5] ~20$ - It does not need to be a exact match, but you will have to modify the code to cover it.
- [Pi Camera](https://www.amazon.com/kuman-Raspberry-Camera-Module-OV5647/dp/B06XKLLT6G/ref=sr_1_5?ie=UTF8&qid=1544007564&sr=8-5&keywords=pi+camera+zero) with connecting tape ~ 16$ - You need specifically this connecting tape for pi zero, as it is different than for other raspberry versions
- [camera case](https://www.amazon.com/components-Latest-Raspberry-Camera-Megapixel/dp/B00IJZJKK4/ref=sr_1_15?ie=UTF8&qid=1544007656&sr=8-15&keywords=pi+camera+case) this camera case, or you can 3Dprint one.
-  - [sunny connector for camera](https://botland.com.pl/moduly-i-zestawy-raspberry-pi-zero/8764-adapter-do-kamery-dla-raspberry-pi-zero.html?search_query=pi+zero&results=64)
- [Li-Pol Redox 900mAh 20C 3S 11,1V](https://botland.com.pl/akumulatory-li-pol-3s-111v-/8320-pakiet-li-pol-redox-900mah-20c-3s-111v.html) - I could not find that part on amazon, but battery with simmilar specs could do, but you might need to change the connector
- [Charger for battery](https://botland.com.pl/ladowarki-lipol-sieciowe/1240-ladowarka-redox-lipo-z-zasilaczem.html)
- [L298N - Dual Drive control](https://www.amazon.com/Qunqi-Controller-Module-Stepper-Arduino/dp/B014KMHSW6/ref=sr_1_1?ie=UTF8&qid=1544008236&sr=8-1&keywords=l298) ~ 7$
-  - Pair of T-DEAN connectors
- for RPI0 [GPIO pins](https://www.amazon.com/DIKAVS-Break-Away-2x20-pin-Header-Raspberry/dp/B075VNBD3R/ref=sr_1_4?ie=UTF8&qid=1544008428&sr=8-4&keywords=gpio+raspberry+pi+zero) you may find already in some raspberry pi zero sets
- some [connecting cables](https://www.amazon.com/Elegoo-EL-CP-004-Multicolored-Breadboard-arduino/dp/B01EV70C78/ref=sr_1_3?ie=UTF8&qid=1544008389&sr=8-3&keywords=gpio+wires)
- something like this [chassis](https://www.amazon.com/d/Robotics-Kit/diymore-Chassis-Encoder-Battery-Arduino/B01LWYUQPH/ref=sr_1_fkmr2_3?ie=UTF8&qid=1544653043&sr=8-3-fkmr2&keywords=chassis+Rectangle+2WD) to mount everythin with a pair of wheels with motors
- something like this [photo interrupter](https://www.amazon.com/Waveshare-Photo-Interrupter-Sensor-Measuring/dp/B01N0FQ21B/ref=sr_1_1?ie=UTF8&qid=1544653159&sr=8-1&keywords=waveshare+photo+interrupter)

## How to build this

### First build the chassis 
This should be pretty intuitive.

### Mount raspberry

I used ot glue and zip-tie. Remember to orient it correct way, and leave the video connector accessible.

### Next mount the camera
Mount Imu as well. Ideally youwant it as close to the camera as possible.
I used some bolts and nuts to mount over front wheel.

![camera-mount-image](https://imgur.com/h7iWKCl.jpg)

**PS**
There is [3D mount](https://github.com/mmajewsk/Tonic/issues/19) availible for 3D printing. Done thanks to [panovv](https://github.com/panovvv)
![camera-mount-vadim](https://i.imgur.com/HBv4bao.jpg?2)


## Mount the battery and on switch
Attach the battery under the chassis. I used a cable tie around PI and created a loop underneath chassis.

![battery-mount](https://imgur.com/JN1e4w5.jpg)

### Mount the drive control and RPI0

I used hot glue. Do not let cables touch the radiatior. Make it as stable as possible.

## Connecting the wires

For the reference to the RPI0 pinout, use [this](https://pinout.xyz/) website. I will use both the board numbering and BCM.
So here is the wiring scheme (**ITS NOT CORRECT - SEE ISSUE [#18](https://github.com/mmajewsk/Tonic/issues/18)** ):

![wiring-scheme-bb](https://imgur.com/DKIMYCb.jpg)
![overall_wires](https://imgur.com/C4JZ7Y8.jpg)

Some components may not match their real counterparts. Don't worry, I will guide through each component.

### PI0 to Camera

This is easy; just lift the plugs a little bit both at camera and PI.
The one on the raspberry is **very ease to break** so be careful, but dont feel bad if you accidentaly will break it. It just happens ;) 

![camera-wiring](https://imgur.com/fBtAxvY.jpg)

### PI0 to L298N
This one is is the trickiest.

Steering pins:

Pin 	|Raspberry BCM 	| L298N
------|---------------|--------
37 	  | BCM 26 	      | ENA
35 	  | BCM 19 	      | IN1
33 	  | BCM 13 	      | IN2
31 	  | BCM 6 	      | IN3
29 	  | BCM 29 	      | IN4
27 	  | BCM 0 	      | ENB



Power:

Pin 	|Raspberry BCM 	| L298N
------|---------------|--------
2 	  | 5v Power 	    | +5V
6 	  | Ground 	      | GND

![wiring-driver-pins](https://imgur.com/das1gKi.jpg)

The colors used on the wiring scheme are coresponding with photos.

### PI0 to encoders

Wiring of the pins and ground are as follow:

Pin 	|Raspberry BCM 	| Encoder
------|---------------|-----------
36 	  | BCM 16 	      | Right Encoder OUT
34 	  | Ground 	      | GND
32 	  | BCM 12 	      | Left Encoder OUT
30 	  | Ground 	      | GND

![encoders-wiring](https://imgur.com/dbG5z4o.jpg)

When it comes to voltage, I just split the cable coming from Pin 4 (5v Power) of RPI0

![encoders-power-split](https://imgur.com/k0W4KPd.jpg)

### PI0 to IMU

Be sure **not to mix those up**. They are a bit confusing. 

Pin 	|Raspberry BCM 	| IMU
------|---------------|---------
1 	  | 3v3 Power 	  | VDD
3 	  | BCM 2 	      | SDA
5 	  | BCM 3 	      | SCL
9 	  | Ground 	      | GND

![IMU-wiring](https://imgur.com/hTLW2rE.jpg)

### L298N to motors

Just connect OUT1 and OUT2 to the right motor, and OUT3 and OUT4 to the left.
If steering does not work properly, try switching cables in the motor.

### L298 to Power

Use power switch on one of the cables. Make sure that they cannot touch anything else.
**If you close the circuit on the battery it might blow up**
I also used t-dean connectors, and unplug it when im transporting the robot.

### L298 to capacitor

Im using 1500 micro-farad 16V capacitor. **Its polarised so make sure to properly orient it, and to put the minus into the ground**
It acts as a stabiliser, its not necessary but greatly improves the stability of the circuit.

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

0. Set up the [RPI0](#device-setup), and [SLAM docker](https://github.com/mmajewsk/orb_slam_py2_docker)
1. callibrate the camera
2. callibrate the IMU
3. Set up the `settings.yml` correctly
4. Set up desired services on the RPI0(Video, Steering, Imu, Odometry), or on laptop (SLAM).
5. Run Tonic 

### Seting up RPI0 and SLAM
For guide for setting up RPI0 look [here](#device-setup).
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
You can find the guide [here](#setting-up-the-raspberry). You have to be running services to access them with Tonic.

## Running Tonic

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

### Turning the services by Tonic (not fully supported)

There was an attempt to simplify the process of turning everything on, you can see the code used to do that in the file `service_run.py`.

# Device Setup

This file will guide throug the usage of the `rpi` folder.
The code was used on Raspberry Pi Zero with WIFI.
It was not tested on any other device.

## Setting up the raspberry

First of all, you need to e connected to the same network as the device that you will be running Tonic on.
There is enough guides on how to connect the RPI to the wifi already so go and find one.
Remember to put the Raspberrys IP into the [settings](#configuring-settings.yml)
If you will do that, you should build the device toghether, as it is inthe [hardware guide](#hardware-guide)

## How to use this

The recommended workflow is to open as many ssh connections from your machine to the RPI as needed and in each ssh run one of the services.
Yes, this is not nice, but unifying everything so it would work as reliably and would be as easy to monitor is not trivial task.

## Video

### Requirements

This service requires **Python 2** [picamera](https://picamera.readthedocs.io), but it should already be in your raspberry.
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



# Setting up SLAM
Create orb slam docker, using [this repo](https://github.com/mmajewsk/orb_slam_py2_docker/) 
