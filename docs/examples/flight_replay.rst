=========================
Example: Flight Replay
=========================

This example requests a past flight from Droneshare, and then "replays" the mission 
by sending waypoints to a vehicle. For safety reasons, the vehicle is replayed at a height of 30 meters.

.. warning:: 

    At time of writing this example fails with an exception in DKYP2: `#355 DKPY2 Can't clear waypoints <https://github.com/dronekit/dronekit-python/issues/355>`_.

.. todo:: Check if `#355 DKPY2 Can't clear waypoints <https://github.com/dronekit/dronekit-python/issues/355>`_ is fixed and re-review example. 

You can specify which mission to replay using a parameter when starting the script (for example, to replay your own local flights).
By default the code gets (and replays) the public `Droneshare mission with ID 101 <http://www.droneshare.com/mission/101>`_. 

.. figure:: flight_replay_example.png

    Droneshare Mission #101



Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`). 

If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python\examples\flight_replay\


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` 
   you wish to use in the ``--connect`` parameter and specifying the mission to replay.

   .. code-block:: bash

       python flight_replay.py --connect 127.0.0.1:14550 --mission_id 101

   .. note::
   
       The command parameters above are the defaults, and may be omitted. These
       connect to SITL on udp port 127.0.0.1:14550 and replay the mission with id 101.

       
.. tip::

    It is more interesting to watch the example above on a map than the console. The topic :ref:`viewing_uav_on_map` 
    explains how to set up *Mission Planner* to view a vehicle running on the simulator (SITL).

On the command prompt you should see (something like):

.. code-block:: bash


    \dronekit-python\examples\flight_replay>flight_replay.py
    Connecting to vehicle on: 127.0.0.1:14550
    >>> ☺APM:Copter V3.4-dev (e0810c2e)
    >>> ☺Frame: QUAD
    JSON downloaded...
    Generating 95 waypoints from replay...
    ...


How it works
============

The example requests the web server for representative points from the flight, parses the JSON response 
and uses that data to generate 100 waypoints. These are then sent to the vehicle.  



Getting the points
------------------

The following simple function asks for the droneshare flight data:

.. code:: python

    def download_messages(mission_id, max_freq = 1.0):
        """Download a public mission from droneshare (as JSON)"""
        f = urllib.urlopen("%s/api/v1/mission/%s/messages.json?max_freq=%s&api_key=%s" % (api_server, mission_id, max_freq, api_key))
        j = json.load(f, object_hook=_decode_dict)
        f.close()
        return j

Some comments:

* ``max_freq`` is used to throttle the messages found in the raw flight data to a lower message rate
* ``_decode_dict`` is a utility function found on stack overflow which extracts usable strings from unicode encoded JSON (see `flight_replay.py <https://github.com/hamishwillee/dronekit-python/blob/master/examples/flight_replay/flight_replay.py>`_ for its implementation).


Setting the new waypoints
-------------------------

If necessary, the example then reduces the number of messages retrieved into a set that can fit on the vehicle (in this case 100 waypoints).

The following code shows how the vehicle writes the received messages as commands (this part of the code is very similar to that
shown in :ref:`example_mission_basic`):

.. code:: python

    print "Generating %s waypoints from replay..." % len(messages)
    cmds = v.commands
    cmds.clear()
    v.flush()
    for i in xrange(0, len(messages)):
        pt = messages[i]
        lat = pt['lat']
        lon = pt['lon']
        # To prevent accidents we don't trust the altitude in the original flight, instead
        # we just put in a conservative cruising altitude.
        altitude = 30.0 # pt['alt']
        cmd = Command( 0,
                       0,
                       0,
                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                       mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                       0, 0, 0, 0, 0, 0,
                       lat, lon, altitude)
        cmds.add(cmd)
    v.flush()


Known issues
============

At time of writing this example fails with an exception. See `#355 DKPY2 Can't clear waypoints <https://github.com/dronekit/dronekit-python/issues/355>`_ for more information.

.. todo:: 

    When example is fixed replace above text with 
    "This example works around the :ref:`known issues in the API <api-information-known-issues>`. 
    Provided that the vehicle is connected and able to arm, it should run through to completion."

  

Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/flight_replay/flight_replay.py>`_):


.. literalinclude:: ../../examples/flight_replay/flight_replay.py
   :language: python
