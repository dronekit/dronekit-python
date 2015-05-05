====================
Running the Examples
====================


With your drone connected via SITL or USB, you can verify the DroneKit installation by running the example apps that come with the source of DroneKit Python.

Start by cloning the DroneKit repo on your machine.
::

    git clone http://github.com/diydrones/droneapi-python.git

Let's run a small example app to verify our connection with the drone:

::

	cd droneapi-python/example/small_demo


Starting MAVProxy
=================

When developing new DroneAPI python code the easiest approach is to run it inside of MAVProxy. 

So launch MAVProxy with the correct options for talking to your vehicle:

Linux computer connected to the vehicle via USB
-----------------------------------------------

::

    mavproxy.py --master=/dev/ttyUSB0

SITL Linux connected to the vehicle via UDP
-------------------------------------------

::

    mavproxy.py

OSX computer connected to the vehicle via USB
---------------------------------------------

::

    mavproxy.py --master=/dev/cu.usbmodem1


Windows computer connected to the vehicle via USB
-------------------------------------------------

::

    mavproxy.py --master=/dev/cu.usbmodem1


For other connection options see the `MAVProxy documentation <http://tridge.github.io/MAVProxy/>`_.

Loading DroneKit
================

The API includes a mavproxy module to allow you to load (and reload) your custom application into mavproxy.

To load the API module run:

::

	MANUAL> module load droneapi.module.api
	DroneAPI loaded
	MANUAL>

We recommend adding this line to the mavproxy startup script in ~/.mavinit.scr.

::

    echo "module load droneapi.module.api" >> ~/.mavinit.scr

Running the example
===================

The first example we will run is a very small application that just reads some vehicle state and then changes the vehicle mode to AUTO (to start following prestored waypoints).

*For all of these examples, please run them initially with a vehicle at your desk with props removed.*

It is probably best to take a look at the python code before running it.

::

	MANUAL> api start small_demo.py
	Mode: VehicleMode:MANUAL
	Location: Location:lat=21.2938874,lon=-157.8501416,alt=0.189999997616,is_relative=None
	Attitude: Attitude:-0.286077767611,-3.01412272453,0.261489063501
	GPS: GPSInfo:fix=1,num_sat=0
	Param: 75.0
	waiting for download
	Requesting 10 waypoints t=Mon Mar 31 09:41:39 2014 now=Mon Mar 31 09:41:39 2014
	Home WP: MISSION_ITEM {target_system : 255, target_component : 0, seq : 0, frame : 0, command : 16, current : 1, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : 21.2921352386, y : -157.848922729, z : 89.1800003052}
	APIThread-0 exiting...
	APM: Non-Nav command ID updated to #255 idx=1
	waypoint 1
	AUTO>

Yay!  The vehicle is now in AUTO mode.

The next demo builds on what you learned here, to actually tell the vehicle to go someplace.