#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2015-2016, 3D Robotics.
mission_import_export.py:

This example demonstrates how to import and export files in the Waypoint format
(http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
The commands are imported into a list, and can be modified before saving and/or
uploading.

Documentation is provided at:
    http://python.dronekit.io/examples/mission_import_export.html
"""


from dronekit import connect, Command
import time

# Set up option parsing to get connection string
import argparse
description = 'Demonstrates mission import/export from a file.'
parser = argparse.ArgumentParser(description=description)
help = ('Vehicle connection target string. '
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

# Check that vehicle is armable.
# This ensures home_location is set (needed when saving WP file)

while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    time.sleep(1)


def readmission(filename):
    """
    Load a mission from a file into a list. The mission definition is in the
    Waypoint file format
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % filename)
    missionlist = []
    with open(filename) as in_file:
        for i, line in enumerate(in_file):
            if i == 0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray = line.split('\t')
                ln_index = int(linearray[0])  # noqa
                ln_currentwp = int(linearray[1])
                ln_frame = int(linearray[2])
                ln_command = int(linearray[3])
                ln_param1 = float(linearray[4])
                ln_param2 = float(linearray[5])
                ln_param3 = float(linearray[6])
                ln_param4 = float(linearray[7])
                ln_param5 = float(linearray[8])
                ln_param6 = float(linearray[9])
                ln_param7 = float(linearray[10])
                ln_autocontinue = int(linearray[11].strip())
                cmd = Command(0, 0, 0, ln_frame, ln_command, ln_currentwp,
                              ln_autocontinue, ln_param1, ln_param2, ln_param3,
                              ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(filename):
    """
    Upload a mission from a file.
    """
    # Read mission from file
    missionlist = readmission(filename)
    print("\nUpload mission from a file: %s" % filename)
    # Clear existing mission from vehicle
    print(' Clear mission')
    cmds = vehicle.commands
    cmds.clear()
    # Add new mission to vehicle
    for command in missionlist:
        cmds.add(command)
    print(' Upload mission')
    vehicle.commands.upload()


def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    return list(cmds)


def save_mission(filename):
    """
    Save a mission in the Waypoint file format
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    print("\nSave mission from Vehicle to file: %s" % filename)
    # Download mission from vehicle
    missionlist = download_mission()
    # Add file-format information
    out_list = ['QGC WPL 110']  # a list of strings
    # Add home location as 0th waypoint
    home = vehicle.home_location
    out_list += '\t'.join(str(x) for x in (0, 1, 0, 16, 0, 0, 0, 0,
                                           home.lat, home.lon, home.alt, 1))
    # Add commands
    for cmd in missionlist:
        out_list += '\t'.join(str(x) for x in
                              (cmd.seq, cmd.current, cmd.frame, cmd.command,
                               cmd.param1, cmd.param2, cmd.param3, cmd.param4,
                               cmd.x, cmd.y, cmd.z, cmd.autocontinue))

    with open(filename, 'w') as out_file:
        print(" Write mission to file: % s" % filename)
        out_file.write('\n'.join(out_list))


def printfile(filename):
    """
    Print a mission file to demonstrate "round trip"
    """
    print("\nMission file: %s" % filename)
    with open(filename) as in_file:
        print('\n'.join(line.strip() for line in in_file))

import_mission_filename = 'mpmission.txt'
export_mission_filename = 'exportedmission.txt'

# Upload mission from file
upload_mission(import_mission_filename)

# Download mission we just uploaded and save to a file
save_mission(export_mission_filename)

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()


print("\nShow original and uploaded/downloaded files:")
# Print original file (for demo purposes only)
printfile(import_mission_filename)
# Print exported file (for demo purposes only)
printfile(export_mission_filename)
