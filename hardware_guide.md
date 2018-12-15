# Tonic Hardware Guide

## List of components


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
- something like [this](https://www.amazon.com/Waveshare-Photo-Interrupter-Sensor-Measuring/dp/B01N0FQ21B/ref=sr_1_1?ie=UTF8&qid=1544653159&sr=8-1&keywords=waveshare+photo+interrupter)

## How to build this

### First build the chassis 
This should be pretty intuitive.

### Mount raspberry

I used ot glue and zip-tie. Remember to orient it correct way, and leave the video connector accessible.

### Next mount the camera
Mount Imu as well. Ideally youwant it as close to the camera as possible.
I used some bolts and nuts to mount it with front wheel.

[camera-mount-image]

[imu-mounted-image]



## Mount the battery and on switch
Attach the battery under the chassis. I used a cable tie around PI and created a loop underneath chassis.

[battery-mount]

### Mount the drive control and RPI0

I used hot glue. Do not let cables touch the radiatior. Make it as stable as possible.

## Connecting the wires

For the reference to the RPI0 pinout, use [this](https://pinout.xyz/) website. I will use both the board numbering and BCM.
So here is the wiring scheme:

[wiring-scheme-bb]

Some components may not match their real counterparts. Don't worry, I will guide through each component.

### PI0 to Camera

This is easy; just lift the plugs a little bit both at camera and PI.
The one on the raspberry is **very ease to break** so be careful, but dont feel bad if you accidentaly will break it. It just happens ;) 

[camera-wiring]

### PI0 to L298N
This one is is the trickiest.

Steering pins:

Pin 	|Raspberry BCM 	| L298N
37 	| BCM 26 	| ENA
35 	| BCM 19 	| IN1
33 	| BCM 13 	| IN2
31 	| BCM 6 	| IN3
29 	| BCM 29 	| IN4
27 	| BCM 0 	| ENB

[wiring-driver-pins]

Power:

Pin 	|Raspberry BCM 	| L298N
2 	| 5v Power 	| +5V
6 	| Ground 	| GND

[wiring-driver-power]

### PI0 to encoders

Wiring of the pins and ground are as follow:

Pin 	|Raspberry BCM 	| Encoder
36 	| BCM 16 	| Right Encoder OUT
34 	| Ground 	| GND
32 	| BCM 12 	| Left Encoder OUT
30 	| Ground 	| GND

[encoders-wiring]

When it comes to voltage, I just split the cable coming from Pin 4 (5v Power) of RPI0

[encoders-power-split]

### PI0 to IMU

Be sure **not to mix those up**. They are a bit confusing. 

Pin 	|Raspberry BCM 	| IMU
1 	| 3v3 Power 	| VDD
3 	| BCM 2 	| SDA
5 	| BCM 3 	| SCL
9 	| Ground 	| GND

[IMU-wiring]

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

[capacitor]



