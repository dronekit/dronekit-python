======================
Fourth Demo: Follow Me
======================

This is a significantly more complex example – showing closed-loop control of the vehicle. It will use a USB GPS attached to your laptop to have the vehicle follow you as you walk around a field.

Run this example with caution - be ready to exit follow-me mode by switching the flight mode switch on your RC radio.

In practice, you don't really want to use this follow-me implementation, rather you can use this example as a starting point to build your own custom application.

Before running this demo you'll need to make sure your computer has the gpsd service installed.

*Ubuntu install*

::

    apt-get install gpsd gpsd-clients

You can then plug in a USB GPS and run the "xgps" client to confirm that it is working. If you do not have a USB GPS you can use simulated data by running *droneapi-python/example/run-fake-gps.sh*.

Once your GPS is plugged in you can start follow-me by running the following command inside of MAVProxy:

::

	RTL> api start follow_me.py
	RTL> Going to: Location:lat=50.616468333,lon=7.131903333,alt=30,is_relative=True
	Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
	GUIDED> Mode GUIDED
	Going to: Location:lat=50.616468333,lon=7.131903333,alt=30,is_relative=True
	Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
	...

These debugging messages will appear every two seconds - when a new target position is sent to the vehicle, to stop follow-me either change the vehicle mode switch on your RC transmitter or type "api stop".

The source code for this example is a good starting point for your own application, from here you can use all python language features and libraries (OpenCV, classes, lots of packages etc...)

Next, take a look at the full :doc:`DroneKit-Python API Reference <automodule>` for more information.

