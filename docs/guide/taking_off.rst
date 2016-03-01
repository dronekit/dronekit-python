.. _taking-off:

==========
Taking Off
==========

This article explains how to get your *Copter* to take off. 

At high level, the steps are: check that the vehicle is *able* to arm, set the mode to ``GUIDED``, 
command the vehicle to arm, takeoff and block until we reach the desired altitude.

.. todo:: 

    Plane apps take off using the ``MAV_CMD_NAV_TAKEOFF`` command in a mission. The plane should first arm and then change to
    ``AUTO`` mode to start the mission. The action here is to add a link when we have an example we can point to.


.. tip::

    Copter is usually started in ``GUIDED`` mode. 
    
    * For Copter 3.2.1 and earlier you cannot take off in ``AUTO`` mode (if you need to run a mission you take off
      in ``GUIDED`` mode and then switch to ``AUTO`` mode once you're in the air).    
    * Starting from Copter 3.3 you can takeoff in ``AUTO`` mode (provided the mission has a 
      `MAV_CMD_NAV_TAKEOFF <http://copter.ardupilot.com/common-mavlink-mission-command-messages-mav_cmd/#copter-2>`_ command)
      but the mission will not start until you explicitly send the 
      `MAV_CMD_MISSION_START <http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_mission_start>`_ 
      message.
      
    By contrast, Plane apps take off using the ``MAV_CMD_NAV_TAKEOFF`` command in a mission. 
    Plane should first arm and then change to ``AUTO`` mode to start the mission. 

The code below shows a function to arm a Copter, take off, and fly to a specified altitude. This is taken from :ref:`example_simple_goto`.

.. code-block:: python

    # Connect to the Vehicle (in this case a simulator running the same computer)
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

    def arm_and_takeoff(aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        vehicle.mode    = VehicleMode("GUIDED")
        vehicle.armed   = True

        # Confirm vehicle armed before attempting to take off
        while not vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print " Altitude: ", vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude. 
            if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
                print "Reached target altitude"
                break
            time.sleep(1)

    arm_and_takeoff(20)


The function first performs some pre-arm checks.

.. note:: 

    Arming turns on the vehicle's motors in preparation for flight. The flight controller will not arm
    until the vehicle has passed a series of pre-arm checks to ensure that it is safe to fly.

These checks are encapsulated by the :py:func:`Vehicle.is_armable <dronekit.Vehicle.is_armable>` 
attribute, which is ``true`` when the vehicle has booted, EKF is ready, and the vehicle has GPS lock. 

.. code-block:: python

        print "Basic pre-arm checks"
        # Don't let the user try to arm until autopilot is ready
        while not vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)
            
.. note::

    If you need more status information you can perform the following sorts of checks:
    
    .. code-block:: python

        if v.mode.name == "INITIALISING":
            print "Waiting for vehicle to initialise"
            time.sleep(1)
        while vehicle.gps_0.fix_type < 2:
            print "Waiting for GPS...:", vehicle.gps_0.fix_type
            time.sleep(1)
            
    You should always do a final check on :py:func:`Vehicle.is_armable <dronekit.Vehicle.is_armable>`!


Once the vehicle is ready we set the mode to ``GUIDED`` and arm it. We then wait until arming is confirmed 
before sending the :py:func:`takeoff <dronekit.Vehicle.simple_takeoff>` command.

.. code-block:: python

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

The ``takeoff`` command is asynchronous and can be interrupted if another command arrives before it reaches 
the target altitude. This could have potentially serious consequences if the vehicle is commanded to move 
horizontally before it reaches a safe height. In addition, there is no message sent back from the vehicle 
to inform the client code that the target altitude has been reached.

To address these issues, the function waits until the vehicle reaches a specified height before returning. If you're not
concerned about reaching a particular height, a simpler implementation might just "wait" for a few seconds.

.. code-block:: python

        while True:
            print " Altitude: ", vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude. 
            if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
                print "Reached target altitude"
                break
            time.sleep(1)

When the function returns the app can continue in ``GUIDED`` mode or switch to ``AUTO`` mode to start a mission.
