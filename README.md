<div align="center">
  
# An open-sourced project of autonomous car 
  
[Introduction](#introduction) • [Documentation](#ok-so-how-do-I-start?) • [Screenshots] • [Contribute](#contribute) 
  
![Tonic logo](https://imgur.com/eh1QMvS.jpg)

![Latest commit](https://img.shields.io/github/last-commit/mmajewsk/tonic/master?style=flat-square)
![Licence](https://img.shields.io/github/license/mmajewsk/tonic)
[![Discord Server](https://img.shields.io/discord/739733971944079401?color=blue&label=Discord%20Chat&logo=discord&logoColor=white&style=flat-square)][Discord]

![demo](https://imgur.com/HAA9xJo.gif)

_a.k.a.: "Roomba, that does not suck"_

Written in Python 🐍 (mostly).


</div>

---

### Contents:

- [Introduction](#introduction)
- [Features](#features.) 
- [How does it work](#how-does-it-work) 
- [How to start](#ok-so-how-do-I-start?)
- [Contribution](#contribution)
- [Related repos](#related-repos)

# Introduction

This repository contains main software and documentation for the Tonic project. This project aims to create an open-sourced autonomous driving system, along with its hardware prototype implementation. Some essential parts of the projects are contained in other related repos. See [the list of related repos](#related-repos)
The core idea of how this should work is as follows:

1. After setting up the robot/car, drive it manually, and dump the video and steering feed (this part is called _data taking_).
2. Create a 3D mapping of the environment with [TonicOrange].
3. Define checkpoints, through which the machine will drive.
4. Program the car to drive on the defined paths.

All of that to be possible for as cheap as possible, with a raspberry PI and only a single camera.

# Features.

  <img src="https://imgur.com/oA3ERWN.gif" width="45%" height="45%" align="right" />

  - Camera live feed and recording.
  - Live steering system and recording.
  - Working IMU live streaming and recording.
  - Working odometry live streaming and recording.
  - Qt GUI client for driving and data taking.
  - SLAM mapping, and navigation implemented with ORB_SLAM2 and its custom fork, custom python bindings, and serialisation.

# How does it work

As for now, this repository ([mmajewsk/Tonic]) contains guides and software for building, running and steering the car 🚘 for the _data taking_.
The code is divided, into [Tonic/remote_control] and [Tonic/car]. 

The [Tonic/remote_control] contains the code that is meant to be run on your laptop/pc/mac, that will control the raspberry pi [Tonic/car].

The machine and control interface is communicating via WiFi network, using sockets. 

Sensors, camera, and steering - each one is implemented as a separate service using sockets.
You can steer it with the keyboard on PC, and with live feed from the camera.
All of the sensors, steering and video can be dumped to files on PC.
You don't need to turn all of the sensors to make this work.

**The odometry and IMU are not necessary to make an environment mapping**

The navigation and autonomous steering part are currently under making on under [TonicOrange] repository.

# Ok so how do I start?

0. Take a look at previous versions and the current one in [video and screenshots][Screenshots].
1. First start by [assembling the hardware](doc/hardware_guide.md).
2. Then set up the [machine and interface software](doc/running_software.md).
3. Do the data-taking run, running steering and video data, [as described here](doc/running_software.md##running-tonic).

To make your machine drive autonomously, follow the soon upcoming guide in [TonicOrange] repo.
  

# Contribution

🧑‍🔧 This project initially is meant to be open for everyone. The contributions are welcome.
If you would like to help see what's new or listed in the issues [here](https://github.com/mmajewsk/Tonic/issues) .

Also, you can join the 🗣️ [discord server](discord) if you are looking for quick help, or just want to say hi ;) 


# Related repos
- [My fork of ORB_SLAM2](https://github.com/mmajewsk/ORB_SLAM2)
- [My fork of Osmap] - Dumps ORB_SLAM2 to file
- [My fork of PythonBindings] - this one combines osmap with orb slam python bindings!
- [TonicSlamDunk] - Install scripts for all of the above, includes scripts for ubuntu, and dockerfile.
- [TonicOrange] - **Exemplary use of orb slam, for pathfinding**
  

[discord]: https://discord.gg/55WuPN
[mmajewsk/Tonic]: https://github.com/mmajewsk/Tonic
[Tonic/remote_control]: https://github.com/mmajewsk/Tonic/remote_control
[Tonic/car]: https://github.com/mmajewsk/Tonic/car
[My fork of ORB_SLAM2]: https://github.com/mmajewsk/ORB_SLAM2
[My fork of Osmap]: https://github.com/mmajewsk/osmap 
[My fork of PythonBindings]: https://github.com/mmajewsk/ORB_SLAM2-PythonBindings 
[TonicSlamDunk]: https://github.com/mmajewsk/TonicSlamDunk 
[TonicOrange]: https://github.com/mmajewsk/TonicOrange 
[Screenshots]: doc/video_and_screenshots.md
