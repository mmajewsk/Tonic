<div align="center">
  [Introduction](#introduction) • [Documentation](#ok-so-how-do-I-start?) • [Screenshots] • [Contribute](#contribute) 
  ![](https://imgur.com/eh1QMvS.jpg)

[![Discord Server](https://img.shields.io/discord/739733971944079401?color=blue&label=Discord%20Chat&logo=discord&logoColor=white&style=flat-square)][Discord]

# An open-sourced project of autonomous car 
(Or just a Roomba, that does not suck ;) )

Written in Python (mostly).


</div>

**Contents:**

1. [Introduction](#introduction)
2. [Features](#features.) 
3. [How does it work](#how-does-it-work) 
4. [How to start](#ok-so-how-do-I-start?)
5. [Contribution](#contribution)
6. [Related repos](#related-repos)


# Introduction

This repository contains main software and documentation for the Tonic project. This project aims to create an open-sourced autonomous driving system, along with it's hardware prototype implementation. Some essential parts of the projects are contained in other related repos. See [the list of related repos](#related-repos)
The core idea for how this should work is as follows:

1. After setting up the robot/car, drive it manually to create a [](3D mapping of the environment) (this part is called __data taking__).
2. Define paths, on which the machine will drive.
3. Program the car to drive on the defined paths.

All of that to be possible for as cheap as possible, with raspberry PI and only single camera.

# Features.
  - Camera live feed and recording.
  - Live steering system and recording.
  - Working IMU live streaming and recording.
  - Working odometry live streaming and recording.
  - QT gui client for driving and data taking.
  - SLAM mapping, and navigation implemented with ORB_SLAM2 and its custom fork, custom python bindings, and serialisation.

# How does it work

As for now, this repository ([mmajewsk/Tonic]) contains hardware build guide, and software for running and steering the car for the **data taking**.
The code is divided, into [Tonic/control_interface] and [Tonic/controlled_machine]. 

The [Tonic/control_interface] contains the code that is meant to be run on your laptop/pc/mac, that will controll the raspberry pi [Tonic/controlled_machine].

The machine and control interface are communicating via WiFi network, using sockets. 

Sensors, camera, and steering - each one is implemented
as a separate service using sockets.
You can steer it with keyboard on PC, and with live feed from camera.
All of the sensors, stearing and video can be dumped to files on PC.
You don't need to turn all of the sensors to make this work.
**The odometry and IMU are not necessesary to make a envrionment mapping**

The navigation and autonomous steering part are currently under making on under [TonicOrange] repository.

# Ok so how do I start?

0. Take a look at previous versions and the current one in [video and screenshots][Screenshots].
1. First start by [assembling the hardware](doc/hardware_build_guide.md).
2. Then setup the [machine and interface software](doc/software_machine_setup.md).
3. Do the data taking run, duming steering and video data, [as described here](doc/software_machine_setup.md##running-tonic).

In order to make your machine drive autonomously, follow the soon upcoming guide in [TonicOrange] repo.
  

# Contribution:

This project initially is meant to be open for everyone. The contributions are welcome.
If you would like to help see what's new or listed in the issues [here](https://github.com/mmajewsk/Tonic/issues).
Also you can join the [discord server](discord) if you are looking for quick help, or just want to say hi ;) 


# Related repos
- [My fork of ORB_SLAM2](https://github.com/mmajewsk/ORB_SLAM2)
- [My fork of Osmap] - Dumps ORB_SLAM2 to file
- [My fork of PythonBindings] - this one combines osmap with orb slam python bindings!
- [TonicSlamDunk] - Install scripts for all of the above, includes scripts for ubuntu, and dockerfile.
- [TonicOrange] - **Examplary use of orb slam, for path finding**
  

[discord]: https://discord.gg/55WuPN
[mmajewsk/Tonic]: https://github.com/mmajewsk/Tonic
[Tonic/control_interface]: https://github.com/mmajewsk/Tonic/control_interface
[Tonic/controlled_machine]: https://github.com/mmajewsk/Tonic/controlled_machine
[My fork of ORB_SLAM2]: https://github.com/mmajewsk/ORB_SLAM2
[My fork of Osmap]: https://github.com/mmajewsk/osmap 
[My fork of PythonBindings]: https://github.com/mmajewsk/ORB_SLAM2-PythonBindings 
[TonicSlamDunk]: https://github.com/mmajewsk/TonicSlamDunk 
[TonicOrange]: https://github.com/mmajewsk/TonicOrange 
[Screenshots]: doc/video_and_screenshots.md
