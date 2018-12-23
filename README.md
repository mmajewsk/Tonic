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



# Setting up

- Follow the [hardware guide](https://github.com/mmajewsk/Tonic/blob/master/hardware_guide.md) 
- Follow the [device setup guide](https://github.com/mmajewsk/Tonic/blob/master/device_setup.md)
- Create orb slam docker, using [this repo](https://github.com/mmajewsk/orb_slam_py2_docker/) 
- Follow the [software setup guide ](https://github.com/mmajewsk/Tonic/blob/master/software_guide.md)
