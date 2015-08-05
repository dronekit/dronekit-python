"""
mission_import_export.py: 

This example demonstrates how to import and export files in the Waypoint file format 
(http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format). The commands are imported
into a list, and can be modified before saving and/or uploading.

Documentation is provided at http://python.dronekit.io/examples/mission_import_export.html
"""

import time
import math
from droneapi.lib import Command
from pymavlink import mavutil

# Connect to API provider and get vehicle
api = local_connect()
vehicle = api.get_vehicles()[0]


def readmission(aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print "Reading mission from file: %s\n" % aFileName
    cmds = vehicle.commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                print ' Import line: %s' % line
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])	
                ln_autocontinue=int(linearray[11].strip())		
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(aFileName):
    """
    Upload a mission from a file. 
    """
    missionlist = readmission(aFileName)
    #clear existing mission
    print 'Clear mission'
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_valid()
    cmds.clear()
    vehicle.flush()
    print 'ClearCount: %s' % cmds.count
    #add new mission
    cmds.download()
    cmds.wait_valid()
    for command in missionlist:
        cmds.add(command)
    vehicle.flush()	


def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_valid()
    for cmd in cmds[1:]:  #skip first item as it is home waypoint.
        missionlist.append(cmd)
    return missionlist

def save_mission(aFileName):
    """
    Save a mission in the Waypoint file format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    missionlist = download_mission()
    output='QGC WPL 110\n'
    for cmd in missionlist:
        commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
        output+=commandline
    with open(aFileName, 'w') as file_:
        file_.write(output)    


import_mission_filename = 'mpmission.txt'
export_mission_filename = 'exportedmission.txt'

print "\nUpload mission from a file: %s" % import_mission_filename		
upload_mission(import_mission_filename)

time.sleep(1)

print "\nSave mission from Vehicle to file: %s" % export_mission_filename
save_mission(export_mission_filename)

