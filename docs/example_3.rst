=========================
Third Demo: Flight Replay
=========================

This is an interesting demo that uses our web API to query raw flight data from a particular flight.


Starting the demo
=================

In this case, we pick some public flight from `Droneshare <http://www.droneshare.com/>`_:

.. image:: https://github.com/diydrones/droneapi-python/raw/master/example/documentation/flight_replay_example.png

You'll notice that the mission number for this flight is 101.

Now we'll launch **flight_replay.py** (/example/flight_replay/flight_replay.py) and ask it to try and 'replay' mission 101.  It will ask the web server for representative points from the flight, parse the JSON response and use that data to generate 100 waypoints we would like our vehicle to hit.  For safety rather than using the altitude from the original flight we instead ask our vehicle to fly at a height of 30 meters.

One possible use of some variant of this tool to replay your old flights at your regular test field.

:: 

	STABILIZE> api start flight_replay.py 101
	STABILIZE> JSON downloaded...
	Genrating 95 waypoints from replay...
	APIThread-1 exiting...
	Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
	Sent waypoint 0 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 0, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 45.7379052, y : 126.6273574, z : 30.0}
	Sent waypoint 1 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 1, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 45.7378905, y : 126.6273609, z : 30.0}
	Sent waypoint 2 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 2, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0,
	...
	Sent waypoint 92 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 92, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 45.737971, y : 126.6274908, z : 30.0}
	Sent waypoint 93 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 93, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 45.738018, y : 126.6275664, z : 30.0}
	Sent waypoint 94 : MISSION_ITEM {target_system : 1, target_component : 1, seq : 94, frame : 3, command : 16, current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 45.7380429, y : 126.6275067, z : 30.0}
	Sent all 95 waypoints
	Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
	APM: flight plan received


How it works
============

Getting the points
------------------

The following simple function asks for the droneshare flight data:

::

	def download_messages(mission_id, max_freq = 1.0):
	    """Download a public mission from droneshare (as JSON)"""
	    f = urllib.urlopen("%s/api/v1/mission/%s/messages.json?max_freq=%s&api_key=%s" % (api_server, mission_id, max_freq, api_key))
	    j = json.load(f, object_hook=_decode_dict)
	    f.close()
	    return j

Some comments:

* ``max_freq`` is used to throttle the messages found in the raw flight data to a lower message rate
* ``_decode_dict`` is a utility function found on stack overflow which extracts usable strings from unicode encoded JSON (see `flight_replay.py <https://github.com/hamishwillee/dronekit-python/blob/master/example/flight_replay/flight_replay.py>`_ for its implementation).


Setting the new waypoints
=========================

We generate up to 100 wpts for the vehicle with the following code:

::

    print "Genrating %s waypoints from replay..." % len(messages)
    cmds = v.commands
    cmds.clear()
    for i in xrange(0, len(messages)):
        pt = messages[i]
        lat = pt['lat']
        lon = pt['lon']
        # To prevent accidents we don't trust the altitude in the original flight, instead
        # we just slam in a conservative crusing altitude
        altitude = 30.0 # pt['alt']
        cmd = mavutil.mavlink.MAVLink_mission_item_message(0,
                                                         0,
                                                         0,
                                                         mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                                                         mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                                         0, 0, 0, 0, 0, 0,
                                                         lat, lon, altitude)
        cmds.add(cmd)
    v.flush()


Next we'll work with existing Linux services (gpsd) to add a new drone based feature called :doc:`Follow Me <example_4>`.
