#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.

channel_overrides.py: 

Demonstrates how set and clear channel-override information.

# NOTE: 
Channel overrides (a.k.a "RC overrides") are highly discommended (they are primarily implemented 
for simulating user input and when implementing certain types of joystick control).

They are provided for development purposes. Please raise an issue explaining why you need them
and we will try to find a better alternative: https://github.com/dronekit/dronekit-python/issues

Full documentation is provided at http://python.dronekit.io/examples/channel_overrides.html
"""
from __future__ import print_function
from dronekit import connect


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Example showing how to set and clear vehicle channel-override information.')
parser.add_argument('--connect', 
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

# Get all original channel values (before override)
print("Channel values from RC Tx:", vehicle.channels)

# Access channels individually
print("Read channels individually:")
print(" Ch1: %s" % vehicle.channels['1'])
print(" Ch2: %s" % vehicle.channels['2'])
print(" Ch3: %s" % vehicle.channels['3'])
print(" Ch4: %s" % vehicle.channels['4'])
print(" Ch5: %s" % vehicle.channels['5'])
print(" Ch6: %s" % vehicle.channels['6'])
print(" Ch7: %s" % vehicle.channels['7'])
print(" Ch8: %s" % vehicle.channels['8'])
print("Number of channels: %s" % len(vehicle.channels))


# Override channels
print("\nChannel overrides: %s" % vehicle.channels.overrides)

print("Set Ch2 override to 200 (indexing syntax)")
vehicle.channels.overrides['2'] = 200
print(" Channel overrides: %s" % vehicle.channels.overrides)
print(" Ch2 override: %s" % vehicle.channels.overrides['2'])

print("Set Ch3 override to 300 (dictionary syntax)")
vehicle.channels.overrides = {'3':300}
print(" Channel overrides: %s" % vehicle.channels.overrides)

print("Set Ch1-Ch8 overrides to 110-810 respectively")
vehicle.channels.overrides = {'1': 110, '2': 210,'3': 310,'4':4100, '5':510,'6':610,'7':710,'8':810}
print(" Channel overrides: %s" % vehicle.channels.overrides) 


# Clear override by setting channels to None
print("\nCancel Ch2 override (indexing syntax)")
vehicle.channels.overrides['2'] = None
print(" Channel overrides: %s" % vehicle.channels.overrides) 

print("Clear Ch3 override (del syntax)")
del vehicle.channels.overrides['3']
print(" Channel overrides: %s" % vehicle.channels.overrides) 

print("Clear Ch5, Ch6 override and set channel 3 to 500 (dictionary syntax)")
vehicle.channels.overrides = {'5':None, '6':None,'3':500}
print(" Channel overrides: %s" % vehicle.channels.overrides) 

print("Clear all overrides")
vehicle.channels.overrides = {}
print(" Channel overrides: %s" % vehicle.channels.overrides) 

#Close vehicle object before exiting script
print("\nClose vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed")
