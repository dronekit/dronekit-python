#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.

channel_overrides.py:

Demonstrates how set and clear channel-override information.

# NOTE:
Channel overrides (a.k.a "RC overrides") are highly discommended (they are
primarily implemented  for simulating user input and when implementing certain
types of joystick control).

They are provided for development purposes. Please raise an issue explaining
why you need them and we will try to find a better alternative:
    https://github.com/dronekit/dronekit-python/issues

Full documentation is provided at:
    http://python.dronekit.io/examples/channel_overrides.html
"""
from dronekit import connect


#Set up option parsing to get connection string
import argparse
description = ('Example showing how to set and clear vehicle channel-override '
               'information.')
parser = argparse.ArgumentParser(description=description)
help = ('vehicle connection target string. '
        'If not specified, SITL automatically started and used.')
parser.add_argument('--connect', help=help)
args = parser.parse_args()

connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
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
print('\n'.join(" Ch%s: %s" % (i, vehicle.channels[str(i)])
                for i in range(1, 9)))
print("Number of channels: %s" % len(vehicle.channels))


# Override channels
print("\nChannel overrides: %s" % vehicle.channels.overrides)

print("Set Ch2 override to 200 (indexing syntax)")
vehicle.channels.overrides['2'] = 200
print(" Channel overrides: %s" % vehicle.channels.overrides)
print(" Ch2 override: %s" % vehicle.channels.overrides['2'])

print("Set Ch3 override to 300 (dictionary syntax)")
vehicle.channels.overrides = {'3': 300}
print(" Channel overrides: %s" % vehicle.channels.overrides)

print("Set Ch1-Ch8 overrides to 110-810 respectively")
vehicle.channels.overrides = {'1': 110, '2': 210, '3': 310, '4': 4100,
                              '5': 510, '6': 610, '7': 710, '8': 810}
print(" Channel overrides: %s" % vehicle.channels.overrides)


# Clear override by setting channels to None
print("\nCancel Ch2 override (indexing syntax)")
vehicle.channels.overrides['2'] = None
print(" Channel overrides: %s" % vehicle.channels.overrides)

print("Clear Ch3 override (del syntax)")
del vehicle.channels.overrides['3']
print(" Channel overrides: %s" % vehicle.channels.overrides)

print("Clear Ch5, Ch6 override and set channel 3 to 500 (dictionary syntax)")
vehicle.channels.overrides = {'5': None, '6': None, '3': 500}
print(" Channel overrides: %s" % vehicle.channels.overrides)

print("Clear all overrides")
vehicle.channels.overrides = {}
print(" Channel overrides: %s" % vehicle.channels.overrides)

# Close vehicle object before exiting script
print("\nClose vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()

print("Completed")
