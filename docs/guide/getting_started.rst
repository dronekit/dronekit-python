.. _get-started:

===============
Getting Started
===============

DroneKit-Python apps are typically run on Linux-based :ref:`companion computers <supported-companion-computers>` that travel on the vehicle and communicate with the autopilot via a serial port. However, it is usually easier to first prototype your app on a standard Mac, Windows, or Linux computer using a simulated autopilot. The instructions in this document apply to both scenarios.

.. tip:: If you want to develop for *DroneKit* on Windows using a simulated autopilot, our :ref:`quick-start` shows how to get up and running fast!


Setting up the vehicle/autopilot
=================================

The topic :ref:`supported-companion-computers` has links to a number of tested hardware/software configurations for onboard Linux computers. These  
include information about how to set up the hardware and physically connect to the vehicle. 

If you wish to use a simulated vehicle, the Software-In-The-Loop (SITL) environment can be used to simulate a Copter, Plane, or Rover. It runs natively on Linux, 
but can also run on Linux hosted in a virtual machine:

* `Setting up SITL on Linux <http://dev.ardupilot.com/wiki/setting-up-sitl-on-linux/>`_ (for Linux).
* :ref:`QuickStart: Set up the simulated vehicle <vagrant-sitl-from-full-image>` (for Windows or Mac OSX). 

  .. note::

      The method used in the QuickStart is fast and reliable because it uses Vagrant to load an image that is pre-built and fully configured with SITL. 
      Other approaches are described in the wiki topics `Setting up SITL using Vagrant <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/setting-up-sitl-using-vagrant/>`_ 
      and `Setting up SITL on Windows <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/setting-up-sitl-on-windows/>`_.



Installing DroneKit
===================

*DroneKit* can be installed on Linux, Windows and Mac OSX. 


Installing DroneKit on Linux
----------------------------

If you are using Ubuntu or Debian Linux you can get most of the *DroneKit* dependencies by running:

.. code:: bash

    sudo apt-get install python-pip python-numpy python-opencv python-serial python-pyparsing python-wxgtk2.8

	
The remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_), are 
installed when you get DroneKit-Python from the public PyPi repository:

.. code:: bash

    sudo pip install droneapi

	

.. tip:: 

    If you are planning to run *DroneKit* on a :ref:`companion computer <supported-companion-computers>`, make sure that the 
    computer runs a variant of Linux that support Python and can install Python packages from the internet.


Installing DroneKit on Mac OSX
------------------------------

If you're on Mac OSX, you can use `Homebrew <http://brew.sh/>`_ to install *WXMac*.

.. code:: bash

    brew install wxmac
	
Uninstall *python-dateutil* (OSX and Windows come bundled with a version that is not supported for some dependencies):

.. code:: bash

    pip uninstall python-dateutil

Install DroneKit-Python and its remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_) from the public PyPi repository:

.. code:: bash

    pip install numpy pyparsing
    pip install droneapi
	


Installing DroneKit on Windows
------------------------------

The easiest way to set up DroneKit-Python on Windows is to use the *WinPython* package, which already includes most of the needed dependencies.
You will need remove *python-dateutil* as the installation comes bundled with a version that does not work with some *DroneKit* dependencies.

The steps to install this package and our add-on modules are:

1. Run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ for your platform (win32 vs win64)

2. Register the python that came from *WinPython* as the preferred interpreter for your machine:

   Open the folder where you installed WinPython, run *WinPython Control Panel* and choose **Advanced/Register Distribution**.

   .. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

3. Install DroneKit-Python and its remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_) from the public PyPi repository:

   Open the *WinPython Command Prompt* and run the following two commands:

   .. code:: bash

	    pip uninstall python-dateutil
	    pip install droneapi


.. _starting-mavproxy:

Starting MAVProxy
=================

Launch *MAVProxy* with the correct options for talking to your vehicle (simulated or real):

.. list-table:: MAVProxy connection options
   :widths: 10 10
   :header-rows: 1

   * - Connection type
     - MAVProxy command
   * - Linux computer connected to the vehicle via USB
     - ``mavproxy.py --master=/dev/ttyUSB0``
   * - Linux computer connected to the vehicle via Serial port (RaspberryPi example)
     - ``mavproxy.py --master=/dev/ttyAMA0 --baudrate 57600``
   * - SITL Linux connected to the vehicle via UDP
     - ``mavproxy.py --master=127.0.0.1:14550``
   * - OSX computer connected to the vehicle via USB
     - ``mavproxy.py --master=/dev/cu.usbmodem1``	 
   * - Windows computer connected to the vehicle via USB
     - ``mavproxy.py --master=/dev/cu.usbmodem1``		 
	    

For other connection options see the `MAVProxy documentation <http://tridge.github.io/MAVProxy/>`_.


.. _loading-dronekit:

Loading DroneKit
================

*DroneKit* is implemented as a *MAVProxy* module. You can automatically load this module into *MAVProxy*
by `adding it to the startup script <http://tridge.github.io/MAVProxy/mavinit.html>`_ (**mavinit.scr**).

Linux/MAC OSX:

.. code:: bash

    echo "module load droneapi.module.api" >> ~/.mavinit.scr

Windows:

.. code:: bash

    echo module load droneapi.module.api >> %HOMEPATH%\AppData\Local\MAVProxy\mavinit.scr
	
	
Alternatively you can choose to manually (re)load *DroneKit* into *MAVProxy* every time you need it:

.. code-block:: bash
   :emphasize-lines: 1

	MANUAL> module load droneapi.module.api
	DroneAPI loaded
	MANUAL>



.. _getting-started-running_examples:

Running an app/example
======================

*DroneKit* is implemented as a *MAVProxy* module. In order to run a *DroneKit* app you first need to :ref:`start MAVProxy <starting-mavproxy>`
(connecting to the autopilot) and :ref:`load DroneKit <loading-dronekit>`.

Once the *MAVProxy* console is running, you can start a script by entering: **api start full_path_and_filename_to_script**. If you started
*MAVProxy* in the same directory as the script you can just specify its filename.

.. warning:: 

    This example doesn't take off, but it does arm the motors. Don't run any example indoors on a real vehicle 
    unless you have first removed its propellers. 

For this example, download :download:`vehicle_state.py <../../examples/vehicle_state/vehicle_state.py>` (the 
:ref:`example <example-vehicle-state>` just reads and writes some :ref:`vehicle state and parameters <vehicle-information>`).
Start *MAVProxy*  in the same directory as **vehicle_state.py**.

The output should look something like that shown below

.. code-block:: bash
   :emphasize-lines: 1

    MANUAL> api start vehicle_state.py
    STABILIZE>

    Get all vehicle attribute values:
     Location:  Attitude: Attitude:pitch=-0.00405988190323,yaw=-0.0973932668567,roll=-0.00393210304901
     Velocity: [0.06, -0.07, 0.0]
     GPS: GPSInfo:fix=3,num_sat=10
     groundspeed: 0.0
     airspeed: 0.0
     mount_status: [None, None, None]
     Mode: STABILIZE
     Armed: False
    Set Vehicle.mode=GUIDED (currently: STABILIZE)
     Waiting for mode change ...
    Got MAVLink msg: COMMAND_ACK {command : 11, result : 0}
    ...



.. _viewing_uav_on_map:

Watching the action
====================

Watching your DroneKit script run inside *MAVProxy* is useful, but you can go one step further and watch the behaviour of your simulated vehicle in *Mission Planner*. 

To do this you first need to get SITL to output to an additional UDP port of your computer:

* Find the network IP address of your Windows computer (you can get this by running *ipconfig* in the *Windows Command Prompt*). 
* In the command prompt *for your simulated environment* (SITL), add the IP address of the host computer (e.g. 192.168.2.10) and an unused port (e.g. 145502) as an output:
  
  .. code:: bash
   
      output add 192.168.2.10:14552

Then connect Mission Planner to this UDP port:  
	  
* `Download and install Mission Planner <http://ardupilot.com/downloads/?did=82>`_
* Ensure the selection list at the top right of the Mission Planner screen says *UDP* and then select the **Connect** button next to it. 
  When prompted, enter the port number (in this case 14552).
  
  .. figure:: MissionPlanner_ConnectPort.png
      :width: 50 %

      Mission Planner: Listen Port Dialog

After connecting, vehicle parameters will be loaded into *Mission Planner* and the vehicle is displayed on the map.