.. _sitl_setup:

=====================================
Setting up a Simulated Vehicle (SITL)
=====================================

The `SITL (Software In The Loop) <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/>`_ 
simulator allows you to create and test DroneKit-Python apps without a real vehicle (and from the comfort of 
your own developer desktop!).

SITL can run natively on Linux, Mac and Windows, or within a virtual machine. It can be 
installed on the same computer as DroneKit, or on another computer on the same network.

The sections below explain how install and run SITL, and how to connect to DroneKit-Python and Ground
Stations at the same time.


DroneKit-SITL
=============

DroneKit-SITL is the simplest, fastest and easiest way to run SITL on Windows, Linux, or MAC OSX.
It is installed from Python's *pip* tool on all platforms, and works by downloading and running pre-built 
vehicle binaries that are appropriate for the host operating system.

This section provides an overview of how to install and use DroneKit-SITL. For more information, see 
the `project on Github <https://github.com/dronekit/dronekit-sitl>`_.

.. note:: 

    DroneKit-SITL is still relatively experimental. There are only a few pre-built vehicles and
    they have not been as well tested as the native builds.  
    Please report any issues on `Github here <https://github.com/dronekit/dronekit-sitl/issues>`_.

Installation
------------

The tool is installed (or updated) on all platforms using the command: 

.. code-block:: bash

    pip install dronekit-sitl -UI

Running SITL
------------

To run the latest version of Copter for which we have binaries (downloading the binaries if needed), you can simply call:

.. code-block:: bash

    dronekit-sitl copter
    
SITL will then start and wait for TCP connections on ``127.0.0.1:5760``.
    
You can specify a particular vehicle and version, and also parameters like the home location, 
the vehicle model type (e.g. "quad"), etc. For example:

.. code-block:: bash

    dronekit-sitl plane-3.3.0 --home=-35.363261,149.165230,584,353
    
There are a number of other useful arguments:

.. code-block:: bash  

    dronekit-sitl -h            #List all parameters to dronekit-sitl.
    dronekit-sitl copter -h     #List additional parameters for the specified vehicle (in this case "copter").
    dronekit-sitl --list        #List all available vehicles.
    dronekit-sitl --reset       #Delete all downloaded vehicle binaries.
    dronekit-sitl ./path [args...]  #Start SITL instance at target file location.


.. note:: 

    DroneKit-SITL also `exposes a Python API <https://github.com/dronekit/dronekit-sitl#api>`_, which you can use to start simulation from within your scripts. This is particularly useful for test code!
        

.. _connecting_dronekit_sitl:

Connecting to (DroneKit-) SITL
------------------------------

SITL waits for TCP connections on ``127.0.0.1:5760``. DroneKit-Python scripts running on the same
computer can connect to the simulation using the connection string as shown:

.. code-block:: python

    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

If you need to connect to DroneKit-Python and a ground station at the same time you will need to
`install MAVProxy <http://dronecode.github.io/MAVProxy/html/getting_started/download_and_installation.html>`_ 
for your system.

Then in a second terminal you spawn an instance of *MAVProxy* to forward messages from
TCP ``127.0.0.1:5760`` to UDP ports ``127.0.0.1:14550`` and ``127.0.0.1:14551`` (this is what **sim_vehicle.sh** does
if you build SITL from source):

.. code-block:: bash

    mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551

You can then connect to a ground station using one UDP address, and DroneKit-Python using the other. 
For example:

.. code-block:: python

    vehicle = connect('127.0.0.1:14550', wait_ready=True)



Building SITL from source
=========================

You can natively build SITL from source on Linux, Windows and Mac OS X, 
or from within a Vagrant Linux virtual environment.

Building from source is useful if you want to need to test the latest changes (or any use 
a version for which DroneKit-SITL does not have pre-built binaries). 
It can also be useful if you have problems getting DroneKit-SITL to work.

The following topics from the ArduPilot wiki explain how:

* `Setting up SITL on Linux <http://dev.ardupilot.com/wiki/setting-up-sitl-on-linux/>`_
* `Setting up SITL on Windows <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/sitl-native-on-windows/>`_ 
* `Setting up SITL using Vagrant <http://dev.ardupilot.com/wiki/setting-up-sitl-using-vagrant/>`_


.. _viewing_uav_on_map:

Connecting an additional Ground Station
=======================================

You can connect a ground station to an unused port to which messages 
are being forwarded. You can forward messages to additional ports 
when you start *MAVProxy* using the using ``-out`` 
parameter (as shown :ref:`above <connecting_dronekit_sitl>`).

Alternatively, once *MAVProxy* is started you can add new output ports in the *MAVProxy* console using: ``output add``:

.. code:: bash

    output add 127.0.0.1:14552

.. note::

    Instead of the loopback address you can also specify the network IP address of your computer
    (On Windows you can get this by running *ipconfig* in the *Windows Command Prompt*).


Then connect Mission Planner to this UDP port:  

* `Download and install Mission Planner <http://ardupilot.com/downloads/?did=82>`_
* Ensure the selection list at the top right of the Mission Planner screen says *UDP* and then select the **Connect** button next to it. 
  When prompted, enter the port number (in this case 14552).
  
  .. figure:: MissionPlanner_ConnectPort.png
      :width: 50 %

      Mission Planner: Listen Port Dialog

After connecting, vehicle parameters will be loaded into *Mission Planner* and the vehicle is displayed on the map.

