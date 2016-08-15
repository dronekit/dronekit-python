from __future__ import print_function

"""
avoidance.py: Demonstrate autopilot collision avoidance functionality

Full documentation is provided at http://python.dronekit.io/examples/avoidance.html
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil
import threading

import dronekit
import mavlink_hub
import sys

#Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Demonstrates autopilot automatic avoidance functionality.')
parser.add_argument('--extra-connection',
                   help="extra MAVLink connections to make.")
parser.add_argument('--test',
                   help="test to run")
parser.add_argument('--binary',
                    help="path to autopilot binary to use")
parser.add_argument('--defaults',
                    help="path to autopilot defaults file to use")
parser.add_argument('--resolution', choices=["TCAS", "RTL", "PERPENDICULAR"],
                    help="Specify resolution behaviour for conflict",
                    default="PERPENDICULAR")
args = parser.parse_args()

# example of a binary path: $HOME/rc/ardupilot/build/sitl-debug/bin/arducopter-quad
# example of a defaults path: $HOME/rc/ardupilot/Tools/autotest/copter_params.parm


sitls = []

hub_thread = None
target_systems = []

hub_connection_strings = []

# units for lat/lon are multiples of ~11 metres from -35.363261 149.165230
tests = [
    { #0
        "vehicle_info": [
            {
                "lat": 0,
                "lon": -2,
                "alt": 10,
                "target-lat": 10,
                "target-lon": -2,
                "target-alt": 10,
                "expected-heading": 270,
            },
            {
                "lat": 12,
                "lon": 0,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 180,
            }
        ]
    },
    { #1
        "vehicle_info": [
            {
                "lat": 0,
                "lon": 2,
                "alt": 10,
                "target-lat": 10,
                "target-lon": 2,
                "target-alt": 10,
                "expected-heading": 90,
            },
            {
                "lat": 12,
                "lon": 0,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 180,
            }
        ]
    },
    { #2 horizontal movement, avoidance LTR, above threat
        "vehicle_info": [
            {
                "lat": 1,
                "lon": 0,
                "alt": 10,
                "target-lat": 1,
                "target-lon": 10,
                "target-alt": 10,
                "expected-heading": 0,
            },
            {
                "lat": 0,
                "lon": 12,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 270,
            }
        ]
    },
    { #3 horizontal movement, avoiding aircraft LTR, below threat
        "vehicle_info": [
            {
                "lat": -1,
                "lon": 0,
                "alt": 10,
                "target-lat": -1,
                "target-lon": 10,
                "target-alt": 10,
                "expected-heading": 180,
            },
            {
                "lat": 0,
                "lon": 12,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 270,
            }
        ]
    },
    { #4 horizontal movement, avoiding aircraft RTL, below threat
        "vehicle_info": [
            {
                "lat": 0,
                "lon": 12,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 360,
            },
            {
                "lat": -1,
                "lon": 0,
                "alt": 10,
                "target-lat": -1,
                "target-lon": 20,
                "target-alt": 10,
                "expected-heading": 90,
            },
        ]
    },


    { #5 threat moves vertically S, we move ENE towards it
        "vehicle_info": [
            {
                "lat": 0,
                "lon": -12,
                "alt": 10,
                "target-lat": 3,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 270,
            },
            {
                "lat": 12,
                "lon": 0,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 180,
            }
        ]
    },
    { #6 threat moves vertically S, we move ESE towards it
        "vehicle_info": [
            {
                "lat": 12,
                "lon": -12,
                "alt": 10,
                "target-lat": 9,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 270,
            },
            {
                "lat": 0,
                "lon": 0,
                "alt": 10,
                "target-lat": 12,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 0,
            }
        ]
    },
    { #7 threat moves N, we move NW towards it
        "vehicle_info": [
            {
                "lat": 3,
                "lon": 12,
                "alt": 10,
                "target-lat": 12,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 90,
            },
            {
                "lat": 0,
                "lon": 0,
                "alt": 10,
                "target-lat": 30,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 0,
            }
        ],
    },
    { #8 threat moves N, we move NE towards it
        "vehicle_info": [
            {
                "lat": 3,
                "lon": -12,
                "alt": 10,
                "target-lat": 12,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 270,
            },
            {
                "lat": 0,
                "lon": 0,
                "alt": 10,
                "target-lat": 22,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 0,
            }
        ],
    },
    { #9 threat moves E, we move NNE
        "vehicle_info": [
            {
                "lat": -8,
                "lon": 6,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 12,
                "target-alt": 10,
                "expected-heading": 180,
            },
            {
                "lat": 0,
                "lon": 0,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 12,
                "target-alt": 10,
                "expected-heading": 90,
            }
        ],
    },


    { #10 threate moves NE, we move SE
        "vehicle_info": [
            {
                "lat": 6,
                "lon": -6,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 309,
            },
            {
                "lat": -6,
                "lon": -6,
                "alt": 10,
                "target-lat": 6,
                "target-lon": 6,
                "target-alt": 10,
                "expected-heading": 39,
            }
        ],
    },
    { #11 threat moves SE, we move NE
        "vehicle_info": [
            {
                "lat": -6,
                "lon": -6,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 230,
            },
            {
                "lat": 6,
                "lon": -6,
                "alt": 10,
                "target-lat": -6,
                "target-lon": 6,
                "target-alt": 10,
                "expected-heading": 140,
            }
        ],
    },
    { #12 threat moves SW, we move SE
        "vehicle_info": [
            {
                "lat": 6,
                "lon": 6,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 50,
            },
            {
                "lat": 6,
                "lon": -6,
                "alt": 10,
                "target-lat": -6,
                "target-lon": 6,
                "target-alt": 10,
                "expected-heading": 140,
            }
        ],
    },


    { #13 threat is stationery, we move SE, BELOW 3D-avoid height
        "vehicle_info": [
            {
                "lat": 1,
                "lon": 6,
                "alt": 10,
                "target-lat": 1,
                "target-lon": -6,
                "target-alt": 10,
                "expected-heading": 73,
            },
            {
                "lat": 0,
                "lon": 0,
                "alt": 10,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 10,
                "expected-heading": 307, # this is kind of random
            }
        ],
    },

    { #14 threat is stationery, we move SE, ABOVE 3D-avoid height
        "vehicle_info": [
            {
                "lat": 1,
                "lon": 15,
                "alt": 50,
                "target-lat": 1,
                "target-lon": -6,
                "target-alt": 60,
                "expected-heading": 72,
            },
            {
                "lat": 0,
                "lon": -0.001,
                "alt": 60,
                "target-lat": 0,
                "target-lon": 0,
                "target-alt": 50,
                "expected-heading": 90,
            }
        ],
    },
]



# ready data for many dronekit-sitl processes
simulation_count = 2
for i in range(0,simulation_count):
    print("Creating simulator (SITL) %d" % (i,))
    from dronekit_sitl import SITL
    sitl = SITL(instance=i, path=args.binary, defaults_filepath=args.defaults, gdb=True)
#    sitl.download('copter', '3.3', verbose=True)
    sitls.append(sitl)
    hub_connection_strings.append(sitl.connection_string())

# start the SITLs one at a time, giving each a unique SYSID_THISMAV
def set_params_target(i, new_sysid, connection_string):
    lat = -35.363261
    lon = 149.165230
    sitl_args = ['--model', 'quad', '--home=%s,%s,584,353' % (lat,lon,) ]
    print("%d: Launching SITL (%s)" % (i,str(sitl_args)))
    sitls[i].launch(sitl_args, await_ready=True, verbose=True, speedup=50,)
    print("Sleeping a little here")
    time.sleep(5)
    print("%d: Connecting to its vehicle 1" % (i,))
    vehicle = dronekit.connect(connection_string, wait_ready=True, target_system=1, heartbeat_timeout=60)
    while vehicle.parameters["SYSID_THISMAV"] != new_sysid:
        print("%d: Resetting its SYID_THISMAV to %d" % (i, new_sysid,))
        vehicle.parameters["SYSID_THISMAV"] = new_sysid
        time.sleep(0.1)

    # set avoidance behaviour to RTL:
    if i == 0:
        print("%d: Setting avoidance parameters" % (i,))

        # enable ADSB:
        vehicle.parameters["ADSB_ENABLE"] = 1
        # enable avoidance:
        vehicle.parameters["AVD_ENABLE"] = 1

        # set the warn radius down to let us see everything on a reasonable scale:
        vehicle.parameters["AVD_W_DIST_XY"] = 30
        vehicle.parameters["AVD_W_DIST_Z"] = 20
        # set the warn horizon down to let us see everything on a reasonable scale:
        vehicle.parameters["AVD_W_TIME"] = 10

        # set the fail radius down to let us see everything on a reasonable scale:
        vehicle.parameters["AVD_F_DIST_XY"] = 20
        vehicle.parameters["AVD_F_DIST_Z"] = 10
        # set the time horizon down to let us see everything on a reasonable scale:
        vehicle.parameters["AVD_F_TIME"] = 10

        vehicle.parameters["AVD_W_ACTION"] = mavutil.mavlink.MAV_COLLISION_ACTION_REPORT
        vehicle.parameters["AVD_W_RCVRY"] = 1
        vehicle.parameters["AVD_F_RCVRY"] = 1
        if args.resolution == "RTL":
            vehicle.parameters["AVD_F_ACTION"] = mavutil.mavlink.MAV_COLLISION_ACTION_RTL
        elif args.resolution == "PERPENDICULAR":
            vehicle.parameters["AVD_F_ACTION"] = mavutil.mavlink.MAV_COLLISION_ACTION_MOVE_PERPENDICULAR
        elif args.resolution == "TCAS":
            vehicle.parameters["AVD_F_ACTION"] = mavutil.mavlink.MAV_COLLISION_ACTION_TCAS

    print("%d: Allowing time for parameter write" % (i,))
    time.sleep(2)
    vehicle.disconnect()

    print("%d: Stop" % (i,))
    sitls[i].stop()

set_params_threads = []
for i in range(0,len(sitls)):
    new_sysid = len(sitls)-i+1
    set_params_threads.append(threading.Thread(target=set_params_target,
                                                 args=(i,new_sysid, hub_connection_strings[i])))
    set_params_threads[-1].start()
    target_systems.append(new_sysid)
#        mav.remove_message_listener(vehicle)
    time.sleep(1) # mavlink not thread safe...

for thread in set_params_threads:
    print("Waiting for thread...")
    thread.join()

print("Sleeping a little to let SITLs go away...")
time.sleep(2)


# create another connection so a GCS can be connected for visualisation
if args.extra_connection:
    hub_connection_strings.append(args.extra_connection)

# dronekit-python (us!) port:
connection_string = "udpout:localhost:2345"
hub_connection_strings.append("udpin:localhost:2345")

hub_should_quit = False


def mavlink_hub_target():
    print("Hub thread starting")
    hub = mavlink_hub.MAVLinkHub(hub_connection_strings)
    hub.init()
    while not hub_should_quit:
        hub.loop()
    print("Hub quitting")
    hub.connection_maintenance_target_should_live = False

print("Starting mavlink_hub thread")
hub_thread = threading.Thread(target=mavlink_hub_target)
hub_thread.start()

# Create a MAVLink connection:
print("Attempting connect to hub (%s)" % (connection_string,))
mav = dronekit.mavlink.MAVConnection(connection_string)
print("Connected")

vehicles = [None] * len(target_systems)
# Connect to the Vehicle
def vehicle_connect_target(mav, id, offset):
    vehicle = dronekit.connect(mav, wait_ready=True, target_system=id)
    vehicles[offset] = vehicle

def dump_vehicle_state(vehicle):
    print(" Autopilot Firmware version: %s" % vehicle.version)
    print("   Major version number: %s" % vehicle.version.major)
    print("   Minor version number: %s" % vehicle.version.minor)
    print("   Patch version number: %s" % vehicle.version.patch)
    print("   Release type: %s" % vehicle.version.release_type())
    print("   Release version: %s" % vehicle.version.release_version())
    print("   Stable release?: %s" % vehicle.version.is_stable())


def print_collision_message(conn, name , m):
    print("Got collision message: %s" % (str(m),))

mav_lock = threading.Lock() # FIXME; move locking into MAVSystem

def arm_and_takeoff(vehicle, aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    # Copter should arm in GUIDED mode
    while vehicle.mode != 'GUIDED':
        print("Setting mode GUIDED")
        mav_lock.acquire()
        vehicle.mode = VehicleMode("GUIDED")
        mav_lock.release()
        time.sleep(0.5)

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print("Arming motors")
        mav_lock.acquire()
        vehicle.armed = True
        mav_lock.release()
        time.sleep(0.5)

    print("Taking off!")
    mav_lock.acquire()
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    mav_lock.release()

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Mode: %s  Altitude: %f" % (str(vehicle.mode), vehicle.location.global_relative_frame.alt,))
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# sleep so we can see the change in map
def watch_things_for_a_while(duration=30):
    start = time.time()

    while time.time() - start < duration:
        for i in range(0,len(vehicles)):
            vehicle = vehicles[i]
            print("Vehicle %d (%s) Lat=%f Lon=%f Alt=%f MODE=%s Hdg=%f" % (target_systems[i], vehicle.mode, vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_relative_frame.alt, str(vehicle.mode), vehicle.heading))
            time.sleep(1)

def vehicle_launcher_target(i):
    arm_and_takeoff(vehicles[i], 5)

def launch_all_vehicles(altitudes):
    launcher_threads = []
    for i in range(0,len(vehicles)):
        print("Launching Vehicle %d:" % (target_systems[i],))
        launcher_threads.append(threading.Thread(target=vehicle_launcher_target,
                                                 args=(i,)))
        launcher_threads[-1].start()
    for thread in launcher_threads:
        print("Waiting for launcher thread...")
        thread.join()

#    speed = 5
#    for i in range(0,len(vehicles)):
#        print("Set default/target airspeed to %d on vehicle %d (%s)" % (target_systems[i],speed, str(target_systems[i])))
#        vehicles[i].airspeed = speed

    while True:
        all_done = True
        for i in range(0, len(vehicles)):
            v_location = vehicles[i].location.global_relative_frame
            print("%d alt: %f" % (i, v_location.alt))
            if v_location.alt < altitudes[i]-2:
                v_location.alt = altitudes[i]
                vehicles[i].simple_goto(v_location)
                all_done = False
        if all_done:
            break
        time.sleep(1)

def relative_lat(increment):
    return -35.363261 + 0.0001 * increment

def relative_lon(increment):
    return 149.165230 + 0.0001 * increment

class TestFailedException(Exception):
    pass


def heading_delta(a, b):
    if a > b:
        delta =  a - b
    else:
        delta = b - a
    if delta > 180:
        if a > 180:
            delta = 360 - a + b
        else:
            delta = 360 - b + a
    return delta

def do_vehicle_connects():
    offset = 0
    connect_threads = []
    for id in target_systems:
        print('Connecting to vehicle with system ID (%d)' % id)
        connect_threads.append(threading.Thread(target=vehicle_connect_target,
                                                         args=(mav,id,offset)))
        connect_threads[-1].start()
        offset += 1
        time.sleep(2) # mav is not thread safe?!

    for thread in connect_threads:
        print("Waiting for connect thread...")
        thread.join()

    for vehicle in vehicles:
        dump_vehicle_state(vehicle)

def position_vehicles(positions):
    print("Launching SITLs")
    for i in range(0,len(sitls)):
        sitl = sitls[i]
        position = positions[i]
        lat = position["lat"]
        lon = position["lon"]
        sitl_args = ['--model', 'quad', '--home=%s,%s,584,353' % (lat,lon,) ]
        sitl.launch(sitl_args, await_ready=True, restart=True, use_saved_data=True, wd=sitl.wd, verbose=True, speedup=2)

    do_vehicle_connects()

    altitudes = []
    for i in range(0,len(vehicles)):
        altitudes.append(positions[i]["alt"])

    launch_all_vehicles(altitudes)

    print("Starting gotos")

    for i in range(0,len(vehicles)):
        position = positions[i]
        lat = position["target-lat"]
        lon = position["target-lon"]
        alt = position["target-alt"]
        print("vehicle %d: doing simple_goto (%s %s %s" % (target_systems[i],lat, lon, alt))
        point = LocationGlobalRelative(lat, lon, alt)
        vehicles[i].simple_goto(point)


def do_heading_test(test):

    positions = []
    for i in range(0,len(sitls)):
        positions.append({ "lat": relative_lat(test["vehicle_info"][i]["lat"]),
                           "lon": relative_lon(test["vehicle_info"][i]["lon"]),
                           "alt": test["vehicle_info"][i]["alt"],
                           "target-lat": relative_lat(test["vehicle_info"][i]["target-lat"]),
                           "target-lon": relative_lon(test["vehicle_info"][i]["target-lon"]),
                           "target-alt": test["vehicle_info"][i]["target-alt"],
        })
    position_vehicles(positions)

    vehicles[0].add_message_listener('COLLISION', print_collision_message)

    vehicles_at_correct_heading_timer = 0
    loop_start_time = time.time()
    success = None
    while success is None:
        all_correct = True
        for i in range(0,len(vehicles)):
            vehicle = vehicles[i]
            print("Vehicle %d (%s) Lat=%f Lon=%f Alt=%f MODE=%s Hdg=%f" % (target_systems[i], vehicle.mode, vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_relative_frame.alt, str(vehicle.mode), vehicle.heading))
            expected = test["vehicle_info"][i]["expected-heading"]
            delta = heading_delta(expected, vehicles[i].heading)

            print("Expecting vehicle %d at heading=%f actual=%f delta=%f" % (i, expected, vehicles[i].heading, delta))
            if delta > 3:
                all_correct = False
        if all_correct:
            if vehicles_at_correct_heading_timer != 0:
                if time.time() - vehicles_at_correct_heading_timer > 5:
                   success = True
                else:
                    time.sleep(1)
            else:
                # start the timer
                vehicles_at_correct_heading_timer = time.time()
                time.sleep(1)
        else:
            vehicles_at_correct_heading_timer = 0
            time.sleep(1)
        timeout = 30
        if time.time() - loop_start_time > timeout:
            success = False

    vehicles[0].remove_message_listener('COLLISION', print_collision_message)

    for i in range(0,len(vehicles)):
        vehicle = vehicles[i]
        vehicle.disconnect()
        sitls[i].stop()

    if not success:
        print("Test failed")
        raise TestFailedException("Test failed")

    print("Success")

def do_disable_test():

    vehicle_info = [
        {
            "lat": 0,
            "lon": -2,
            "alt": 10,
            "target-lat": 10,
            "target-lon": -2,
            "target-alt": 10,
        },
        {
            "lat": 12,
            "lon": 0,
            "alt": 10,
            "target-lat": 0,
            "target-lon": 0,
            "target-alt": 10,
        }
    ]

    positions = []
    for i in range(0,len(sitls)):
        positions.append({ "lat": relative_lat(vehicle_info[i]["lat"]),
                           "lon": relative_lon(vehicle_info[i]["lon"]),
                           "alt": vehicle_info[i]["alt"],
                           "target-lat": relative_lat(vehicle_info[i]["target-lat"]),
                           "target-lon": relative_lon(vehicle_info[i]["target-lon"]),
                           "target-alt": vehicle_info[i]["target-alt"],
        })

    global success
    success = True
    def mode_watcher(conn, name , m):
        global success
        if vehicles[0].mode != "GUIDED":
            print("mode is not GUIDED: %s" % (str(vehicles[0].mode)));
            success = False;

    position_vehicles(positions)

    vehicles[0].add_message_listener('HEARTBEAT', mode_watcher)

    # turn off avoidance (vehicle is already flying!)
    vehicles[0].parameters['CH8_OPT'] = 38
    vehicles[0].channels.overrides[8] = 30

    # just wait
    start = time.time()
    while success == True and time.time() - start < 30:
        time.sleep(1)

    for i in range(0,len(vehicles)):
        vehicle = vehicles[i]
        vehicle.disconnect()
        sitls[i].stop()

    if not success:
        print("Test failed")
        raise TestFailedException("Test failed")

    print("Success")


if False:

    do_disable_test()

else:
    if args.test is not None:
        try:
            do_heading_test(tests[int(args.test)])
        except TestFailedException as e:
            print("Test {} Failed: {}".format(int(args.test), str(e)))
    else:
        count=0
        for test in tests:
            print("Doing test #%d" % (count,))
            try:
                do_heading_test(test)
            except TestFailedException as e:
                print("Test {} Failed: {}".format(count, str(e)))
                break
            count += 1
    
print("All done")

if hub_thread is not None:
    hub_should_quit = True
    hub_thread.join()
