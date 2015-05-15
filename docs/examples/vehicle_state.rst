======================
Example: Vehicle State
======================

This little demonstration just tells the vehicle to fly to a couple of different locations in the world.  You can edit the code to pick a latitude and longitude close to your position.

Running the example
===================

Once Mavproxy is running and the API is loaded, you can run this small example by typing: ``api start simple_goto.py``

It will tell your vehicle to start flying to a particular latitude and longitude stored in the file (though for safety the take-off command is not included - you must manually tell vehicle to fly).  On the mavproxy console you should see:

::

	STABILIZE> api start simple_goto.py
	STABILIZE> Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
	GUIDED> Mode GUIDED
	APIThread-0 exiting...
	Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}


How does it work?
=================

The key code in this demo is the following:

::

	vehicle.mode    = VehicleMode("GUIDED")
	origin          = Location(-34.364114, 149.166022, 30, is_relative=True)

	commands.goto(origin)
	vehicle.flush()

It tells the vehicle to fly to a specified lat/long and hover at that location (30 meters in the air).  ``is_relative=True`` is the default and is recommended - it means that the altitude (30 meters) is *relative* to the vehicle home location.  If you had set ``is_relative`` to ``false``, it would have told the vehicle to fly to a specified mean-sea-level which is probably not what you want unless you are next to an ocean.


Building on the basic vehicle control you just learned, we now show how to write a small web application that allows you to command a drone to fly to a particular location.


Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/diydrones/dronekit-python/blob/master/example/simple_goto/simple_goto.py>`_):
	
.. literalinclude:: ../../example/vehicle_state/vehicle_state.py
   :language: python
	
	
	
SOME NOTES/EXAMPLES TO KEEP
===========================

NOTE - annoying timeout setting in parameter
Get named vehicle parameters
Read param THR_MIN: 10.0
timeout setting THR_MIN to 10.000000
Read param THR_MIN: 10.0
Read param THR_MIN: 10.0

MENTION VERY ANNOYING BUG WHEN THERE IS A DELAY - in observer

# Another callback example - this time "generic"
def attribute_callback(attribute):
    print "Generic callback - '%s' changed: %s" % (attribute, getattr(v, attribute) )
	

# Set callback observer for mode
v.add_attribute_observer('armed', attribute_callback)	






################
	


#NOTES
#YOu can't set armed in AUTO
#YOu can't switch back to AUTO mode if you are armed?
#YOu don't get an error for setting armed if in a mode you can't do it. So you need to check. 
# Removed cmds.next - this should go in another example
		
		
#print "Disarming..."
#v.armed = False
#v.flush()

#Bugs
#Perhaps report these in the documentation for the example? Include heartbeat bug.

##################################

Include missing bits that 

##  Generic message handler
##   NOTE: Use of set_mavlink_callback is not recommended. Use add_attribute_observer instead where possible.
##         Observer commented out below because at time of writing there is no way to turn it off!

def mavrx_debug_handler(message):
    """A demo of receiving raw MAVLink messages"""
    print "[Script] Received", message

#print "[Script] Display all MAVLink messages"
#v.set_mavlink_callback(mavrx_debug_handler)


Missing 



"""

print "Disarming..."
v.armed = False
v.flush()
while v.armed and not api.exit:
    print "Waiting for disarming..."
    time.sleep(1)


print "Arming..."
v.armed = True
v.flush()
while not v.armed and not api.exit:
    print "Waiting for arming..."
    time.sleep(1)
	
	
# Example callback for when Vehicle.armed changes
def armed_callback(attribute):
    print "Armed-state changed: ", v.armed

# Add observer for Vehicle.armed parameter		
v.add_attribute_observer('armed', armed_callback)

print "Disarming..."
v.armed = False
v.flush()
while v.armed and not api.exit:
    print "Waiting for disarming..."
    time.sleep(1)


print "Arming..."
v.armed = True
v.flush()
while not v.armed and not api.exit:
    print "Waiting for arming..."
    time.sleep(1)

v.remove_attribute_observer('armed', armed_callback)




print "ADDING ATT OBSERVER"		
v.add_attribute_observer('mode', attribute_callback)
time.sleep(5)
print "Now change the vehicle into AUTO mode"		
v.mode = VehicleMode("AUTO")
v.flush()
time.sleep(5)
print "MYMODE SHOULD BE AUTO:", v.mode

print "Now change the vehicle into STABILIZE mode"
v.mode = VehicleMode("STABILIZE")
v.flush()
time.sleep(5)

v.remove_attribute_observer('mode', attribute_callback)
print "ending in 5"
time.sleep(5)
print "ended"

# Now download the vehicle waypoints
cmds = v.commands
cmds.download()
cmds.wait_valid()
print "Home WP: %s" % cmds[0]
print "Current dest: %s" % cmds.next

"""




Scratchpad


# Change the vehicle into GUIDED mode
print " CHANGE TO GUIDED MODE" 
print " Initial mode: %s" % v.mode.name
v.mode = VehicleMode("GUIDED")
# Always call flush to guarantee that previous writes to the vehicle have taken place
v.flush()

while not v.mode.name=='GUIDED' and not api.exit:
    print " mode: %s" % v.mode.name
    print " Waiting for guided..."
    time.sleep(1)


	
# Change the vehicle into AUTO mode
print " CHANGE TO AUTO MODE" 
print " Initial mode: %s" % v.mode.name
v.mode = VehicleMode("AUTO")
# Always call flush to guarantee that previous writes to the vehicle have taken place
v.flush()

while not v.mode.name=='AUTO' and not api.exit:
    print " mode: %s" % v.mode.name
    print " Waiting for AUTO..."
    time.sleep(1)
	
	
# Change the vehicle into STABILIZE mode
print " CHANGE TO STABILIZE MODE" 
print " Initial mode: %s" % v.mode
v.mode = VehicleMode("STABILIZE")
# Always call flush to guarantee that previous writes to the vehicle have taken place
v.flush()

while not v.mode.name=='STABILIZE' and not api.exit:
    print " mode: %s" % v.mode.name
    print "Waiting for stabilize..."
    time.sleep(1)
	
	
	
print "NEW TEST"

print " Set mode GUIDED - current %s" % v.mode.name
v.mode = VehicleMode("GUIDED")
v.flush()
print " Set mode AUTO - current %s" % v.mode.name
v.mode = VehicleMode("AUTO")
v.flush()
print " Set mode STABILIZE - current %s" % v.mode.name
v.mode = VehicleMode("STABILIZE")
v.flush()	
print " Set mode GUIDED - current %s" % v.mode.name
v.mode = VehicleMode("GUIDED")
v.flush()
print " DONE current %s" % v.mode.name
time.sleep(1)
print " DONE current %s" % v.mode.name
time.sleep(1)
print " DONE current %s" % v.mode.name
time.sleep(1)
print " DONE current %s" % v.mode.name
time.sleep(1)
print " DONE current %s" % v.mode.name

print " Arming vehicle..."
v.armed = True
v.flush()



-------
print "  New Mode: %s" % v.mode
time.sleep(5)
print " Arming vehicle..."
v.armed = True
v.flush()
print "  Armed: %s" % v.armed
time.sleep(5)
print " Disarming vehicle..."
v.armed = False
v.flush()
print "  Armed: %s" % v.armed

time.sleep(5)




print "Disarming..."
v.armed = False
v.flush()

#remove observer
v.remove_attribute_observer('armed', attribute_callback)

print 'ENDED'