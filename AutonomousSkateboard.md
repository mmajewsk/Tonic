# AutonomousSkateboard

This repository will contain notes on the autnomous skateboard.

# Motivation 

It's cheap. It can move a person around. Can be upgraded to auotonomy. What else do you need? 

# Simmilar work

Hacksmith did a remotely controlled board like that (timestamp points to specific) so I know it's possible, but they dida that with 4 motors.
https://www.youtube.com/watch?v=1g5nzRINaPQ&t=368s
Question is will 2 motors be enough to turn the board around?

# Hardware

If you are not familliar with DIY e-skateboards i suggest watching some videos on this topic [like this one  ](https://www.youtube.com/watch?v=LJqyWRSqOy4).

There are multiple parts availible online to buy and assemble, but the cheapest option is to recycle.
I bought [Nillox Longboard](https://www.nilox.com/es/datasheet/electric-skateboard-30nxskmolo001) for mere ~100€.
It was described as broken, but the description suggested tha the battery and wheels are ok, so I risked buying it.

The battery is 4,4 Ah 36V 10s2p with BMS (Battery Management System) built-in.
The motors are 90mm motors (kind of like [these](https://www.amazon.com/PROMOTOR-Motors-Electronic-Skateboard-Longboard/dp/B07F2Y22Q9?th=1)). I don'thave much details but will work this out.

The internal electronic was kind of fine (the problem with the board not working was only with the remote control itself), but still for better control I needed an ESC (electric speed control).

This is where the wonderful, glorious [VESC](https://vesc-project.com/) project comes in.
TL; DR; its highly customisable, open-source elecetric speed control.
I bought 2x flipsky's version of [VESC](https://flipsky.net/products/torque-esc-vesc-%C2%AE-bldc-electronic-speed-controller) (2x one per motor).

# Controlling the speed

The two VESCs can be connected together to duplicate the steering signal.
The VESC can be connected to mobile app or PC via bluetooth (using a proprietary [bluetooth module](https://flipsky.net/products/core51822-ble4-0-bluetooth-2-4g-wireless-module-nrf51822-onboard-ws82013)]. So that's a nice wireless connection.
The main problem is that VESC was not designed with differential steering (we need to move one wheel faster then the other to make it turn) in mind.
There are two possible sollutions:
 - Use external connection to controll VESCs with PWM (pulse-width modulation), so something like arduino would work
 - Dig into the VESC code to find if it's possible to send a different command to the connected vesc than just to repeat. And modify the code to do so.
 So far I'm opting for the second one since it should be more elegant and versatile, but the first one is far easier to implement, but needs additional hardware.
