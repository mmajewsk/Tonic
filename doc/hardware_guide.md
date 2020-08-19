# Hardware Guide

## Before you start


![current_version](https://i.imgur.com/HBv4bao.jpg?2)

Remember that all you really need for this to work is steering and camera, and the IMU and odomoetry are optional. 
This entire hardware guide is __just a guide__. 

It is also a little bit outdated. The picture above presents the [Mark-4] version of the build, but the guide was created with [Mark-3].
This guid is still valid.

 - Since it was created I have changed the version of the raspberry PI to A+
 - And also changed the orientation of the camera (now the two wheels are front, and single one is on the back, as per this picture)
 - Thanks to [panovv](https://github.com/panovvv) the camera is now mounted with a [3D printed mount](https://github.com/mmajewsk/Tonic/issues/19), cad files of which you can find in the repository.
 
Feel free to modify your build.
If you can please reach me and send me pictures of your build, or your version of the guide ;)

## Lists of components, and versions

I have listed two versions of the components: 

- [Mark-3]
- [Mark-4]

This hardware guide was created with pictures from Mark-3, but is valid also for Mark-4 (except the camera mount).
The main difference between Mark-3 and Mark-4 is that Mark-4 uses Raspberry PI A+, and wide angle camera.
This change helped with stability of the process of data taking and mapping, but is slightly more expensive (+30$).
Either way, if you plan on using this project a lot, I highly recommend buying spare parts, as things can sometimes just stop working.
Especially the camera connectors, they keep dying on monthly basis :/ .

**Warning** You will be working with Li-Po batterries, please be safe and careful. Ideally read first this very nice post that explains how they work https://rogershobbycenter.com/lipoguide

## How to build this

### First assmble the chassis 
This should be pretty intuitive. But you can check out [this video](https://www.youtube.com/watch?v=H78t6dnSoG0).

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

[Mark-3]: tonic_mark_3_components.md
[Mark-4]: tonic_mark_4_components.md
