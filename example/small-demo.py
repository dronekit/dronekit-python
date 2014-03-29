from droneapi.lib import VehicleMode

api = local_connect()
v = api.get_vehicles()[0]
print "Mode: %s" % v.mode
print "Location: %s" % v.location
print "Attitude: %s" % v.attitude
print "GPS: %s" % v.gps_0
print "Param: %s" % v.parameters['THR_MAX']
print "Home WP: %s" % v.commands[0]
v.mode = VehicleMode("AUTO")
v.flush()
