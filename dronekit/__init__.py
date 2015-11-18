from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
import dronekit.lib
from dronekit.lib import APIException
from dronekit.mavlink import MAVConnection
from dronekit.util import errprinter
from pymavlink import mavutil, mavwp
from Queue import Queue, Empty
from threading import Thread
import types

# Public re-exports
Vehicle = dronekit.lib.Vehicle
Command = dronekit.lib.Command
CommandSequence = dronekit.lib.CommandSequence
VehicleMode = dronekit.lib.VehicleMode
SystemStatus = dronekit.lib.SystemStatus
LocationGlobalRelative = dronekit.lib.LocationGlobalRelative
LocationGlobal = dronekit.lib.LocationGlobal
LocationLocal = dronekit.lib.LocationLocal
CloudClient = dronekit.lib.CloudClient

def connect(ip, _initialize=True, wait_ready=None, status_printer=errprinter, vehicle_class=Vehicle, rate=4, baud=115200, heartbeat_timeout=30, source_system=255):
    handler = MAVConnection(ip, baud=baud, source_system=source_system)
    vehicle = vehicle_class(handler)

    if status_printer:
        @vehicle.on_message('STATUSTEXT')
        def listener(self, name, m):
            status_printer(re.sub(r'(^|\n)', '>>> ', m.text.rstrip()))
    
    if _initialize:
        vehicle.initialize(rate=rate, heartbeat_timeout=heartbeat_timeout)

    if wait_ready:
        if wait_ready == True:
            vehicle.wait_ready(True)
        else:
            vehicle.wait_ready(*wait_ready)

    return vehicle
