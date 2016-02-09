.. _example_mission_import_export:

==============================
Example: Mission Import/Export
==============================

This example shows how to import and export files in the 
`Waypoint file format <http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format>`_.

The commands are first imported from a file into a list and then uploaded to the vehicle.
Then the current mission is downloaded from the vehicle and put into a list, which is then 
saved into (another file). Finally, we print out both the original and new files
for comparison

The example does not show how missions can be modified, but once the mission is in a list, 
changing the order and content of commands is straightforward.

The guide topic :ref:`auto_mode_vehicle_control` provides information about 
missions and AUTO mode.


Running the example
===================

The example can be run as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`installing_dronekit`).

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python/examples/mission_import_export/

#. You can run the example against a simulator (DroneKit-SITL) by specifying the Python script without any arguments.
   The example will download SITL binaries (if needed), start the simulator, and then connect to it:

   .. code-block:: bash

       python mission_import_export.py

   On the command prompt you should see (something like):
   
   .. code:: bash

       Starting copter simulator (SITL)
       SITL already Downloaded.
       Connecting to vehicle on: tcp:127.0.0.1:5760
       >>> APM:Copter V3.3 (d6053245)
       >>> Frame: QUAD
       >>> Calibrating barometer
       >>> Initialising APM...
       >>> barometer calibration complete
       >>> GROUND START
        Waiting for vehicle to initialise...
        Waiting for vehicle to initialise...
        Waiting for vehicle to initialise...
        Waiting for vehicle to initialise...
        Waiting for vehicle to initialise...
        Reading mission from file: mpmission.txt
        Upload mission from a file: mpmission.txt
        Clear mission
        Upload mission
        Save mission from Vehicle to file: exportedmission.txt
        Download mission from vehicle
       >>> flight plan received
        Write mission to file
       Close vehicle object
        Show original and uploaded/downloaded files:
 
        Mission file: mpmission.txt
        QGC WPL 110
        0  1   0   16  0   0   0   0   -35.363262  149.165237  584.000000  1
        1  0   0   22  0.000000    0.000000    0.000000    0.000000    -35.361988  149.163753  00.000000  1
        2  0   0   16  0.000000    0.000000    0.000000    0.000000    -35.361992  149.163593  00.000000  1
        3  0   0   16  0.000000    0.000000    0.000000    0.000000    -35.363812  149.163609  00.000000  1
        4  0   0   16  0.000000    0.000000    0.000000    0.000000    -35.363768  149.166055  00.000000  1
        5  0   0   16  0.000000    0.000000    0.000000    0.000000    -35.361835  149.166012  00.000000  1
        6  0   0   16  0.000000    0.000000    0.000000    0.000000    -35.362150  149.165046  00.000000  1

        Mission file: exportedmission.txt
        QGC WPL 110
        0    1     0     16    0     0     0     0     -35.3632621765  149.165237427   583.989990234   1
        1    0     0     22    0.0   0.0   0.0   0.0   -35.3619880676  149.163757324   100.0   1
        2    0     0     16    0.0   0.0   0.0   0.0   -35.3619918823  149.163589478   100.0   1
        3    0     0     16    0.0   0.0   0.0   0.0   -35.3638114929  149.163604736   100.0   1
        4    0     0     16    0.0   0.0   0.0   0.0   -35.3637695312  149.166061401   100.0   1
        5    0     0     16    0.0   0.0   0.0   0.0   -35.3618354797  149.166015625   100.0   1
        6    0     0     16    0.0   0.0   0.0   0.0   -35.3621482849  149.165039062   100.0   1


   .. note:: 

       The position values uploaded and then downloaded above do not match exactly. This rounding error can be ignored 
       because the difference is much smaller than the precision provided by GPS. 
    
       The error occurs because all the params are encoded as 32-bit floats rather than 64-bit doubles (Python's native datatype).

#. You can run the example against a specific connection (simulated or otherwise) by passing the :ref:`connection string <get_started_connect_string>` for your vehicle in the ``--connect`` parameter. 

   For example, to connect to SITL running on UDP port 14550 on your local computer:

   .. code-block:: bash

       python mission_import_export.py --connect 127.0.0.1:14550
     

How does it work?
=================

The :ref:`source code <example_mission_import_export_source_code>` is largely self-documenting. 

More information about the functions can be found in the guide at 
:ref:`auto_mode_load_mission_file` and :ref:`auto_mode_save_mission_file`.



Known issues
============

There are no known issues with this example.
  


.. _example_mission_import_export_source_code:
  
Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/mission_import_export/mission_import_export.py>`_):

.. literalinclude:: ../../examples/mission_import_export/mission_import_export.py
   :language: python

