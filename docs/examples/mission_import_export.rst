.. _example_mission_import_export:

==============================
Example: Mission Import/Export
==============================

This example shows how to import and export files in the 
`Waypoint file format <http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format>`_.

.. warning:: 

    At time of writing this example fails with an exception in DKYP2: `#355 DKPY2 Can't clear waypoints <https://github.com/dronekit/dronekit-python/issues/355>`_.

.. todo:: 

    Check if `#355 DKPY2 Can't clear waypoints <https://github.com/dronekit/dronekit-python/issues/355>`_ is fixed and re-review example. 

The commands are first imported from a file into a list and then uploaded to the vehicle.
Then the current mission is downloaded from the vehicle and put into a list, and finally 
saved into (another file).

The example does not show how missions can be modified, but once the mission is in a list, 
changing the order and content of commands is straightforward.

The guide topic :ref:`auto_mode_vehicle_control` provides information about 
missions and AUTO mode.


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`).

If you're using a simulated vehicle, remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run.

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/mission_import_export/


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python mission_import_export.py --connect 127.0.0.1:14550

  
   .. note::
   
       The command parameter above is the default, and may be omitted. This
       connects to SITL on udp port 127.0.0.1:14550.

       

On the command prompt you should see (something like):


.. code:: bash

    Connecting to vehicle on: 127.0.0.1:14550
    >>> APM:Copter V3.4-dev (e0810c2e)
    >>> Frame: QUAD
    Link timeout, no heartbeat in last 5 seconds

    Upload mission from a file: mpmission.txt
    Reading mission from file: mpmission.txt

    STABILIZE>  Import line: 0      1       0       16      0       0       0       0       -35.360500      149.172363      747.000000      1

     Import line: 1 0       3       22      0.000000        0.000000        0.000000        0.000000     -35.359831 149.166334      100.000000      1


     Import line: 2 0       3       16      0.000000        0.000000        0.000000        0.000000     -35.363489 149.167213      100.000000      1

     Import line: 3 0       3       16      0.000000        0.000000        0.000000        0.000000     -35.355491 149.169595      100.000000      1

     Import line: 4 0       3       16      0.000000        0.000000        0.000000        0.000000     -35.355071 149.175839      100.000000      1

     Import line: 5 0       3       113     0.000000        0.000000        0.000000        0.000000     -35.362666 149.178715      22222.000000    1
     Import line: 6 0       3       115     2.000000        22.000000       1.000000        3.000000     0.000000   0.000000        0.000000        1

     Import line: 7 0       3       16      0.000000        0.000000        0.000000        0.000000     0.000000   0.000000        0.000000        1

    Clear mission
    Requesting 9 waypoints t=Wed Jul 29 20:12:17 2015 now=Wed Jul 29 20:12:17 2015
    ClearCount: 0
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    Requesting 0 waypoints t=Wed Jul 29 20:12:17 2015 now=Wed Jul 29 20:12:17 2015
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    Sent waypoint 0 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 0, frame : 0, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.3632621765, y : 149.165237427, z : 584.0}
    Sent waypoint 1 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 1, frame : 0, command : 16, current : 1, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.3605, y : 149.172363, z : 747.0}
    Sent waypoint 2 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 2, frame : 3, command : 22, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.359831, y : 149.166334, z : 100.0}
    Sent waypoint 3 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 3, frame : 3, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.363489, y : 149.167213, z : 100.0}
    Sent waypoint 4 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 4, frame : 3, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.355491, y : 149.169595, z : 100.0}
    Sent waypoint 5 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 5, frame : 3, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.355071, y : 149.175839, z : 100.0}
    Sent waypoint 6 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 6, frame : 3, command : 113, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : -35.362666, y : 149.178715, z : 22222.0}
    Sent waypoint 7 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 7, frame : 3, command : 115, current : 0, autocontinue : 1, param1 : 2.0, param2 : 22.0, param3 : 1.0, param4 : 3.0, x : 0.0, y : 0.0, z : 0.0}
    Sent waypoint 8 : MISSION_ITEM {target_system : 1, target_component : 0, seq : 8, frame : 3, command : 16, current : 0, autocontinue : 1, param1 : 0.0, param2 : 0.0, param3 : 0.0, param4 : 0.0, x : 0.0,y : 0.0, z : 0.0}
    Sent all 9 waypoints   
    Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
    APM: flight plan received

    Save mission from Vehicle to file: exportedmission.txt
    Requesting 9 waypoints t=Wed Jul 29 20:12:18 2015 now=Wed Jul 29 20:12:18 2015
    APIThread-1 exiting...



How does it work?
=================

The :ref:`source code <example_mission_import_export_source_code>` is largely self-documenting. 

More information about the functions can be found in the guide at 
:ref:`auto_mode_load_mission_file` and :ref:`auto_mode_save_mission_file`.



Known issues
============

* This example fails in DroneKit 2.0.0b6 and earlier 
  (see `#355 DKPY2 Can't clear waypoints  <https://github.com/dronekit/dronekit-python/issues/355>`_ to see if it has been fixed).
* A ``time.sleep(1)`` has been placed between uploading the mission to the vehicle (from the file) and downloading the mission. 
  This is to avoid the race condition where the mission being downloaded has not yet successfully uploaded to the vehicle. 
  This race condition (probably) shouldn't exist because the mission is flushed to the Vehicle - 
  see `Race condition when updating and fetching commands <https://github.com/dronekit/dronekit-python/issues/227>`_


 
.. todo:: 

    This is blocked by https://github.com/dronekit/dronekit-python/issues/355 (vehicle.commands.clear not working).
    The code output in "running the example"" needs to be updated once this runs cleanly.
    The above text for the error needs to be replaced with original text 
    
    > "This example works around known issues in the API:."
    
    Need to check all that clearing is still strictly necessary in DKPY2 which handles race conditions more gracefully.


  
  

.. _example_mission_import_export_source_code:
  
Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/mission_import_export/mission_import_export.py>`_):

.. literalinclude:: ../../examples/mission_import_export/mission_import_export.py
   :language: python

