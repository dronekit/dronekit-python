.. _quick_start_top:

===========
Quick Start
===========

This topic shows how to quickly install a DroneKit-Python 
*development environment* and run a simple example to get 
vehicle attributes from a *simulated* Copter.


Installation
============

DroneKit-Python and the *dronekit-sitl simulator* are installed 
from **pip** on all platforms.

On Linux you will first need to install **pip** and **python-dev**:
    
.. code-block:: bash

    sudo apt-get install python-pip python-dev

    
**pip** is then used to install *dronekit* and *dronekit-sitl*.
Mac and Linux may require you to prefix these commands with ``sudo``:

.. code-block:: bash

    pip install dronekit
    pip install dronekit-sitl

See :doc:`../develop/installation` and `dronekit-sitl <https://github.com/dronekit/dronekit-sitl#dronekit-sitl>`_ 
for more detailed installation instructions.


Basic "Hello Drone"
===================

The script below first launches the simulator. It then 
imports and calls the :py:func:`connect() <dronekit.connect>` method, 
specifying the simulator's connection string (``tcp:127.0.0.1:5760``). 
The method returns a :py:class:`Vehicle <dronekit.Vehicle>` object that 
we then use to query the attributes.

.. code:: python

    print "Start simulator (SITL)"
    from dronekit_sitl import SITL
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353']
    sitl.launch(sitl_args, await_ready=True, restart=True)

    # Import DroneKit-Python
    from dronekit import connect, VehicleMode

    # Connect to the Vehicle. 
    print "Connecting to vehicle on: 'tcp:127.0.0.1:5760'"
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

    # Get some vehicle attributes (state)
    print "Get some vehicle attribute values:"
    print " GPS: %s" % vehicle.gps_0
    print " Battery: %s" % vehicle.battery
    print " Last Heartbeat: %s" % vehicle.last_heartbeat
    print " Is Armable?: %s" % vehicle.is_armable
    print " System status: %s" % vehicle.system_status.state
    print " Mode: %s" % vehicle.mode.name    # settable

    # Close vehicle object before exiting script
    vehicle.close()

    # Shut down simulator
    sitl.stop()
    print("Completed")


Copy the text above into a new text file (**hello.py**) and run it in the same way
as you would any other standalone Python script. 

.. code-block:: bash

    python hello.py

You should see the following output from the simulated vehicle:

.. code-block:: bash

    Start simulator (SITL)
    Downloading SITL from http://dronekit-assets.s3.amazonaws.com/sitl/copter/sitl-win-copter-3.3.tar.gz
    Extracted.
    Connecting to vehicle on: 'tcp:127.0.0.1:5760'
    >>> APM:Copter V3.3 (d6053245)
    >>> Frame: QUAD
    >>> Calibrating barometer
    >>> Initialising APM...
    >>> barometer calibration complete
    >>> GROUND START
    Get some vehicle attribute values:
     GPS: GPSInfo:fix=3,num_sat=10
     Battery: Battery:voltage=12.587,current=0.0,level=100
     Last Heartbeat: 0.713999986649
     Is Armable?: False
     System status: STANDBY
     Mode: STABILIZE
    Completed

That's it- you've run your first DroneKit-Python script.

Next Steps
==========

* Learn more about :doc:`../develop/index`. 
  This covers development best practices and coding standards,
  and has more information about installation, working with a simulator 
  and setting up a companion computer.
* Read through our step by step :doc:`index` to learn how to connect to your
  vehicle, takeoff, fly, and much more.
* Check out our :doc:`../examples/index`.
