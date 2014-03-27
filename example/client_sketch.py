# Python highlevel sketch

import DroneApi

## Getting an API instance
# You connect to a particular API implementation by using one of the factory methods...

# api = DroneApi.web_connect(username, password)
api = DApi.local_connect()

## Getting a vehicle instance
# You can get a list of controllable/monitorable vehicles by using one of the following methods

# Get all vehicles user has access to (may be capped in the web case)
# includeOffline is an optional param, if true non connected vehicles will be included (for historical purposes)
# if includeLive is true, currently connected vehicles will be included
vehicles = api.get_vehicles()
v = vehicles[0]

# Get all vehicles user has access to and within the specified rectangle
# vehicles = api.getVehicles(lat1, lon1, lat2, lon2, includeOffline = False)
# Not supported in release 0/1:
# v = api.createVehicle(vehicleId, vehicleType, notes)

## Working with vehicles
# Once you have a vehicle you can do a bunch of interesting things with it.

print v.location
print v.attitude
print v.airspeed
print v.groundspeed

# get battery level etc...
print v.battery_0_soc
print v.battery_0_volt
v.rc_overrides = [ 1000, 1000, 0, 1500 ]
v.flush()
print v.rc_channels

print v.mode
v.mode = "AUTO"
v.goto(location)
wpts = v.waypoints

## Getting missions (to see historical data or read/create live mavlink traffic)

# where logId is either a log id or ‘recent’ for most recent log, or ‘current’ for the current live log
# flight logs are streams of annotated mavlink messages.  The flightlog object also includes metadata
# about that flight.
# m = v.get_mission(logId)

# Operations for uploading mavlink from GCSes/vehicles
# m = v.createMission(‘notes’)
# m.uploadMavlink(timestampedPackets)
# m.endMission()

# Delete the mission
# m.delete()

# The complete set of mavlink messages (mostly useful in case of historical logs)
# packets = m.getMavlink()
# Callback will be invoked asynchronously for each new mavlink message received
# v.set_mavlink_callback(callback)

location = v.location
v.add_attribute_observer("location", callback)

modes = m.getMode

# To send raw mavlink to a vehicle
v.send_mavlink(packet)

# Wait for all previously queued async (reactive) operations to acknowledge)
v.flush()

# For release 2 add GPIO/ADC operations (needs vehicle code)
v.ap_pin5_mode = "adc"
v.flush()
print v.ap_pin5_value
v.ap_pin6_mode = "dac"
v.ap_pin6_value = 2.4
v.flush()

v.ap_pin7_mode = "dout"
v.ap_pin7_value = 1
v.flush()

