.. _auto_mode_vehicle_control:

==============================
Missions (AUTO Mode)
==============================

AUTO mode is used run pre-defined waypoint missions on Copter, Plane and Rover. 

DroneKit-Python provides basic methods to download and clear the current mission commands 
from the vehicle, to add and upload new mission commands, to count the number of waypoints, 
and to read and set the currently executed mission command. 
You can build upon these basic primitives to create high-level mission planning functionality.

This section shows how to use the basic methods and provides a few useful helper functions.
Most of the code can be observed running in :ref:`example_mission_basic` and :ref:`example_mission_import_export`.

.. note::

    We recommend that you :ref:`use GUIDED mode <guided_mode_copter>` instead of AUTO mode where possible, because it offers finer 
    and more responsive control over movement, and can emulate most mission planning activities.

    AUTO mode can be helpful if a command you need is not supported in GUIDED mode on a particular vehicle type.


.. _auto_mode_supported_commands: 

Mission Command Overview
==========================

The mission commands (e.g. ``MAV_CMD_NAV_TAKEOFF``, ``MAV_CMD_NAV_WAYPOINT`` ) supported for each vehicle type are listed here: 
`Copter <http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#commands_supported_by_copter>`_, 
`Plane <http://plane.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#commands_supported_by_plane>`_, 
`Rover <http://rover.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#commands_supported_by_rover>`_.

There are three types of commands:

* *NAVigation commands* (``MAV_CMD_NAV_*``) are used to control vehicle movement, 
  including takeoff, moving to and around waypoints, changing altitude, and landing.
* *DO commands* (``MAV_CMD_DO_*``) are for auxiliary functions that do not affect the vehicle’s position 
  (for example, setting the camera trigger distance, or setting a servo value).
* *CONDITION commands* (``MAV_CMD_NAV_*``) are used to delay *DO commands* until some condition is met. 
  For example ``MAV_CMD_CONDITION_DISTANCE`` will prevent DO commands executing until the vehicle 
  reaches the specified distance from the waypoint.

During a mission at most one *NAV* command and one *DO* or *CONDITION* command can be running **at the same time**.
*CONDITION* and *DO* commands are associated with the last *NAV* command that was sent: if the UAV reaches the waypoint before these 
commands are executed, the next *NAV* command is loaded and they will be skipped.

The `MAVLink Mission Command Messages (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd>`_ 
wiki topic provides a more detailed overview of commands.

.. note:: 

    * If the autopilot receives a command that it cannot handle, then the command will be (silently) dropped.
    * You cannot yet determine dynamically what commands are supported. We hope to deliver this functionality in
      the forthcoming `capability API <https://github.com/dronekit/dronekit-python/issues/250>`_.


.. _auto_mode_download_mission: 

Download current mission
========================

The mission commands for a vehicle are accessed using the :py:attr:`Vehicle.commands <dronekit.Vehicle.commands>` 
attribute. The attribute is of type :py:class:`CommandSequence <dronekit.CommandSequence>`, a class that provides ‘array style’ indexed access to the 
waypoints which make up the mission.

Waypoints are not downloaded from vehicle until :py:func:`download() <dronekit.CommandSequence.download>` is called. The download is asynchronous; 
use :py:func:`wait_ready() <dronekit.CommandSequence.wait_ready>` to block your thread until the download is complete:

.. code:: python

    # Connect to the Vehicle (in this case a simulated vehicle at 127.0.0.1:14550)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

    # Download the vehicle waypoints (commands). Wait until download is complete.
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

.. note::

    In DroneKit-Python 2 :py:attr:`Vehicle.commands <dronekit.Vehicle.commands>` contains just the editable waypoints (in version 1.x, the 
    commands included the non-editable home location as the first item).



.. _auto_mode_clear_mission: 

Clearing current mission
========================

To clear a mission you call :py:func:`clear() <dronekit.CommandSequence.clear>` and then 
:py:func:`Vehicle.commands.upload() <dronekit.Vehicle.commands.upload>` (to upload the changes to the vehicle):

.. code:: python

    # Connect to the Vehicle (in this case a simulated vehicle at 127.0.0.1:14550)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)
    
    # Get commands object from Vehicle.
    cmds = vehicle.commands

    # Call clear() on Vehicle.commands and upload the command to the vehicle.
    cmds.clear()
    cmds.upload()

.. note:: 

    If a mission that is underway is cleared, the mission will continue to the next waypoint. If you don't add a new command
    before the waypoint is reached then the vehicle mode will change to RTL (return to launch) mode.



.. _auto_mode_adding_command: 

Creating/adding mission commands
================================

After :ref:`downloading <auto_mode_download_mission>` or :ref:`clearing <auto_mode_clear_mission>` a mission new commands 
can be added and uploaded to the vehicle. Commands are added to the mission using :py:func:`add() <dronekit.CommandSequence.add>`
and are sent to the vehicle (either individually or in batches) using :py:func:`upload() <dronekit.Vehicle.commands.upload>`.

Each command is packaged in a :py:class:`Command <dronekit.Command>` object (see that class for the order/meaning of the parameters). 
The supported commands for each vehicle are :ref:`linked above <auto_mode_supported_commands>`. 


.. code:: python

    # Connect to the Vehicle (in this case a simulated vehicle at 127.0.0.1:14550)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

    # Get the set of commands from the vehicle
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

    # Create and add commands
    cmd1=Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10)
    cmd2=Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 10, 10, 10)
    cmds.add(cmd1)
    cmds.add(cmd2)
    cmds.upload() # Send commands



.. _auto_mode_modify_mission: 

Modifying missions
==================

While you can :ref:`add new commands <auto_mode_adding_command>` after :ref:`downloading a mission <auto_mode_download_mission>` 
it is not possible to directly modify and upload existing commands in ``Vehicle.commands`` (you can modify the commands but 
changes do not propagate to the vehicle).

.. todo:: test above statement. Might not be true in DKPY2. Also check if we can flush items in a cycle.

Instead you copy all the commands into another container (e.g. a list), 
modify them as needed, then clear ``Vehicle.commands`` and upload the list as a new mission:

.. code:: python

    # Connect to the Vehicle (in this case a simulated vehicle at 127.0.0.1:14550)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)
    
    # Get the set of commands from the vehicle
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()

    # Save the vehicle commands to a list
    missionlist=[]
    for cmd in cmds:
        missionlist.append(cmd)

    # Modify the mission as needed. For example, here we change the 
    # first waypoint into a MAV_CMD_NAV_TAKEOFF command. 
    missionlist[0].command=mavutil.mavlink.MAV_CMD_NAV_TAKEOFF

    # Clear the current mission (command is sent when we call upload()) 
    cmds.clear()

    #Write the modified mission and flush to the vehicle
    for cmd in missionlist:
        cmds.add(cmd)
    cmds.upload()


The changes are not guaranteed to be complete until 
:py:func:`upload() <dronekit.Vehicle.commands.upload>` is called on the parent ``Vehicle.commands`` object.


.. _auto_mode_monitoring_controlling: 

Running and monitoring missions
===============================

To start a mission, change the mode to AUTO:

.. code:: python

    # Connect to the Vehicle (in this case a simulated vehicle at 127.0.0.1:14550)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

    # Set the vehicle into auto mode
    vehicle.mode = VehicleMode("AUTO")

.. note:: 

    If the vehicle is in the air, then changing the mode to AUTO is all that is required to start the 
    mission. 

    **Copter 3.3 release and later:** If the vehicle is on the ground (only), you will additionally need to send the
    `MAV_CMD_MISSION_START <http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_mission_start>`_ 
    command.

You can stop/pause the current mission by switching out of AUTO mode (e.g. into GUIDED mode). If you switch back to 
AUTO mode the mission will either restart at the beginning or resume at the current waypoint - the behaviour depends on the value of the 
`MIS_RESTART <http://copter.ardupilot.com/wiki/arducopter-parameters/#mission_restart_when_entering_auto_mode_mis_restart>`_ 
parameter (available on all vehicle types).

You can monitor the progress of the mission by polling the :py:func:`Vehicle.commands.next <dronekit.CommandSequence.next>` attribute
to get the current command number. You can also change the current command by setting the attribute to the desired command number.

.. code:: python

    vehicle.commands.next=2
    print "Current Waypoint: %s" % vehicle.commands.next
    vehicle.commands.next=4
    print "Current Waypoint: %s" % vehicle.commands.next

There is no need to ``upload()`` changes to send an update to the  ``next`` attribute to the vehicle 
(and as with other attributes, if you fetch a value, it is updated from the vehicle).


.. _auto_mode_handle_mission_end: 

Handling the end of a mission
===============================

At the end of the mission the vehicle will enter LOITER mode (hover in place for Copter, 
circle for Plane, stop for Rover). You can add new commands to the mission, but you will need to toggle from/back to
AUTO mode to start it running again.

Currently there is no notification in DroneKit when a mission completes. If you need to detect mission end (in order
to perform some other operation) then you can either:

* Add a dummy mission command and poll :py:func:`Vehicle.commands.next <dronekit.CommandSequence.next>` for the 
  transition to the final command, or
* Compare the current position to the target position in the final waypoint.




.. _auto_mode_useful_functions: 

Useful Mission functions
========================

This example code contains a number of functions that might be useful for managing and monitoring missions:

.. _auto_mode_load_mission_file: 

Load a mission from a file
-----------------------------

``upload_mission()`` uploads a mission from a file. 

The implementation calls ``readmission()`` (below) to import the mission from a file into a list. The method then
clears the existing mission and uploads the new version. 

Adding mission commands is discussed :ref:`here in the guide <auto_mode_adding_command>`.

.. code:: python

    def upload_mission(aFileName):
            """
            Upload a mission from a file. 
            """
            #Read mission from file
            missionlist = readmission(aFileName)
            
            print "\nUpload mission from a file: %s" % import_mission_filename
            #Clear existing mission from vehicle
            print ' Clear mission'
            cmds = vehicle.commands
            cmds.clear()
            #Add new mission to vehicle
            for command in missionlist:
                cmds.add(command)
            print ' Upload mission'
            vehicle.commands.upload()


``readmission()`` reads a mission from the specified file and returns a list of :py:class:`Command <dronekit.Command>` objects. 

Each line is split up. The first line is used to test whether the file has the correct (stated) format. 
For subsequent lines the values are stored in a :py:class:`Command <dronekit.Command>` object 
(the values are first cast to the correct ``float`` and ``int`` types for their associated parameters).
The commands are added to a list which is returned by the function.
  
.. code:: python

    def readmission(aFileName):
        """
        Load a mission from a file into a list.

        This function is used by upload_mission().
        """
        print "Reading mission from file: %s\n" % aFileName
        cmds = vehicle.commands
        missionlist=[]
        with open(aFileName) as f:
            for i, line in enumerate(f):
                if i==0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                else:
                    linearray=line.split('\t')
                    ln_index=int(linearray[0])
                    ln_currentwp=int(linearray[1])
                    ln_frame=int(linearray[2])
                    ln_command=int(linearray[3])
                    ln_param1=float(linearray[4])
                    ln_param2=float(linearray[5])
                    ln_param3=float(linearray[6])
                    ln_param4=float(linearray[7])
                    ln_param5=float(linearray[8])
                    ln_param6=float(linearray[9])
                    ln_param7=float(linearray[10])
                    ln_autocontinue=int(linearray[11].strip())
                    cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                    missionlist.append(cmd)
        return missionlist



.. _auto_mode_save_mission_file: 

Save a mission to a file
------------------------

``save_mission()`` saves the current mission to a file (in the `Waypoint file format <http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format>`_).	
It uses ``download_mission()`` (below) to get them mission, and then writes the list line-by-line to the file.
  
.. code:: python

    def save_mission(aFileName):
        """
        Save a mission in the Waypoint file format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
        """
        missionlist = download_mission()
        output='QGC WPL 110\n'
        for cmd in missionlist:
            commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
            output+=commandline
        with open(aFileName, 'w') as file_:
            file_.write(output)      

``download_mission()`` downloads the :py:attr:`Vehicle.commands <dronekit.Vehicle.commands>` from the vehicle and 
adds them to a list. Downloading mission is discussed :ref:`in the guide <auto_mode_download_mission>`.

.. code:: python

    def download_mission():
        """
        Downloads the current mission and returns it in a list.
        It is used in save_mission() to get the file information to save.
        """
        missionlist=[]
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()
        for cmd in cmds:
            missionlist.append(cmd)
        return missionlist


  
 

.. _auto_mode_mission_distance_to_waypoint: 

Get distance to waypoint
------------------------

``distance_to_current_waypoint()`` returns the distance (in metres) to the next waypoint:

.. code:: python

    def distance_to_current_waypoint():
        """
        Gets distance in metres to the current waypoint. 
        It returns None for the first waypoint (Home location).
        """
        nextwaypoint=vehicle.commands.next
        if nextwaypoint ==0:
            return None
        missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
        lat=missionitem.x
        lon=missionitem.y
        alt=missionitem.z
        targetWaypointLocation=LocationGlobalRelative(lat,lon,alt)
        distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint

The function determines the current target waypoint number with :py:func:`Vehicle.commands.next <dronekit.CommandSequence.next>`
and uses it to index the commands to get the latitude, longitude and altitude of the target waypoint. The ``get_distance_metres()`` function
(see :ref:`guided_mode_copter_useful_conversion_functions`) is then used to calculate and return the (horizontal) distance 
from the current vehicle location.

.. tip:: 

    This implementation is very basic. It assumes that the next command number is for a valid NAV command (it might not be)
    and that the lat/lon/alt values are non-zero. It is however a useful indicator for test code.



.. _auto_mode_mission_useful_links: 

Useful Links
=================

* `MAVLink mission command messages <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd>`_ (all vehicle types - wiki).

