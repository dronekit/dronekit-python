.. _taking-off:

==========
Taking Off
==========

This article explains how to get your *Copter* to take off. At high level, the steps are: set the mode to ``GUIDED``, 
arm the vehicle, and then call :py:func:`Vehicle.commands.takeoff() <droneapi.lib.CommandSequence.takeoff>`.  

.. todo:: 

    Plane apps take off using the ``MAV_CMD_NAV_TAKEOFF`` command in a mission. The plane should first arm and then change to
    ``AUTO`` mode to start the mission. The action here is to add a link when we have an example we can point to.


.. tip::

    Copter is always started in ``GUIDED`` mode. Copter will not take off ``AUTO`` mode even if you have a 
    `MAV_CMD_NAV_TAKEOFF <http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#copter-2>`_ waypoint 
    in your mission (you can run a mission by switching to ``AUTO`` mode after you're in the air).

The code below shows a function to arm a Copter, take off, and fly to a specified altitude. This is taken from :ref:`example_simple_goto`.

.. code-block:: python

    api = local_connect()
    vehicle = api.get_vehicles()[0]

    def arm_and_takeoff(aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print "Basic pre-arm checks"
        # Don't let the user try to fly autopilot is booting
        if vehicle.mode.name == "INITIALISING":
            print "Waiting for vehicle to initialise"
            time.sleep(1)
        while vehicle.gps_0.fix_type < 2:
            print "Waiting for GPS...:", vehicle.gps_0.fix_type
            time.sleep(1)
		
        print "Arming motors"
        # Copter should arm in GUIDED mode
        vehicle.mode    = VehicleMode("GUIDED")
        vehicle.armed   = True
        vehicle.flush()

        while not vehicle.armed and not api.exit:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude
        vehicle.flush()

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.commands.takeoff will execute immediately).
        while not api.exit:
            print " Altitude: ", vehicle.location.alt
            if vehicle.location.alt>=aTargetAltitude*0.95: #Just below target, in case of undershoot.
                print "Reached target altitude"
                break;
            time.sleep(1)

    arm_and_takeoff(3)
	

The function first performs some pre-arm checks.

.. note:: 

    Arming turns on the vehicle's motors in preparation for flight. The flight controller will not arm
    until the vehicle has passed a series of pre-arm checks to ensure that it is safe to fly.

DroneKit-Python can't check every possible symptom that might prevent arming, but we can confirm that the 
vehicle has booted and has a GPS lock:

.. code-block:: python

    if v.mode.name == "INITIALISING":
        print "Waiting for vehicle to initialise"
        time.sleep(1)
    while vehicle.gps_0.fix_type < 2:
        print "Waiting for GPS...:", vehicle.gps_0.fix_type
        time.sleep(1)

Once the vehicle is ready we set the mode to ``GUIDED`` and arm it. We then call :py:func:`flush() <droneapi.lib.Vehicle.flush>`
to guarantee that the commands have been sent, and then wait until arming is confirmed before sending the 
:py:func:`takeoff <droneapi.lib.CommandSequence.takeoff>` command.

.. code-block:: python
	
    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True
    vehicle.flush()

    while not vehicle.armed and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude
    vehicle.flush()

The ``takeoff`` command is asynchronous and can be interrupted if another command arrives before it reaches 
the target altitude. This could have potentially serious consequences if the vehicle is commanded to move 
horizontally before it reaches a safe height. In addition, there is no message sent back from the vehicle 
to inform the client code that the target altitude has been reached.

To address these issues, the function waits until the vehicle reaches a specified height before returning. If you're not
so concerned about reaching a particular height, a simpler implementation might just "wait" for a few seconds.
	
.. code-block:: python	

    while not api.exit:
        print " Altitude: ", vehicle.location.alt
        if vehicle.location.alt>=aTargetAltitude*0.95: #Just below target, in case of undershoot.
            print "Reached target altitude"
            break;
        time.sleep(1)

When the function returns the app can continue in ``GUIDED`` mode or switch to ``AUTO`` mode to start a mission.