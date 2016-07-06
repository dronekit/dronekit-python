#!/usr/bin/python

import dronekit
import dronekit_sitl
import time


lat = 49.2778638
lon = -123.0633418

sitl = dronekit_sitl.SITL()
sitl.download('copter', '3.3', verbose=True)
sitl_args = ['-I0', '--model', 'quad', '--home={0},{1},584,353'.format(lat, lon)]
sitl.launch(sitl_args, await_ready=True, restart=True)
connection_string = 'tcp:127.0.0.1:5760'


vehicle = dronekit.connect(connection_string, wait_ready=True)

# Don't let the user try to arm until autopilot is ready
while not vehicle.is_armable:
  print(" Waiting for vehicle to initialise... (GPS={0}, Battery={1})".format(vehicle.gps_0, vehicle.battery))
  time.sleep(1)

# Set vehicle mode
desired_mode = 'STABILIZE'
while vehicle.mode != desired_mode:
  vehicle.mode = dronekit.VehicleMode(desired_mode)
  time.sleep(0.5)

while not vehicle.armed:
    print("Arming motors")
    vehicle.armed = True
    time.sleep(0.5)

while True:
  vehicle.channels.overrides[3] = 2000
  print " Ch3 override: %s" % vehicle.channels.overrides[3]

  if vehicle.location.global_relative_frame.alt >= 140: 
    print('Reached target altitude: {0:.2f}m'.format(vehicle.location.global_relative_frame.alt))
    break
  else:
    print("Altitude: {0:.2f}m".format(vehicle.location.global_relative_frame.alt))
  time.sleep(0.5)
