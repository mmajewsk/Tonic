![](https://imgur.com/uKuppcF.jpg)

# Autonomous Intelligent Car 

I present to You, the autonomous car, (almost) entirely written in Python.

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
  
  **Attention! This is cool!** ORB-slam working on the camera deed:
  
  [![Second version (video)](https://img.youtube.com/vi/XR-vKycwOm8/0.jpg)](https://www.youtube.com/watch?v=XR-vKycwOm8)
  
  **C A R E F U L! This is cool as well** 2D map from the video feed:
  
  [![Second version (video)](https://img.youtube.com/vi/Wd5jEd4hx6U/0.jpg)](https://www.youtube.com/watch?v=Wd5jEd4hx6U)
  
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


## Mount the battery and on switch
Attach the battery under the chassis. I used a cable tie around PI and created a loop underneath chassis.

![battery-mount](https://imgur.com/JN1e4w5.jpg)

### Mount the drive control and RPI0

I used hot glue. Do not let cables touch the radiatior. Make it as stable as possible.

## Connecting the wires

For the reference to the RPI0 pinout, use [this](https://pinout.xyz/) website. I will use both the board numbering and BCM.
So here is the wiring scheme:

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



# Setting up
- Follow the [device setup guide](https://github.com/mmajewsk/Tonic/blob/master/device_setup.md)
- Create orb slam docker, using [this repo](https://github.com/mmajewsk/orb_slam_py2_docker/) 
- Follow the [software setup guide ](https://github.com/mmajewsk/Tonic/blob/master/software_guide.md)
