.. _get-started:

===============
Getting Started
===============

DroneKit-Python apps are typically run on Linux-based *companion computers* that travel 
on the vehicle and communicate with the autopilot via a serial port. However, during development it is usually easier to 
prototype apps on a standard Mac, Windows, or Linux computer using a *simulated* autopilot. 


This topic explains how to set up and run DroneKit-Python (within MAVProxy) on the different host operating systems
and then run a basic DroneKit app. 




Setting up the vehicle/autopilot
================================

For information on how to set up a vehicle (real and simulated) see:

* :ref:`supported-companion-computers` for links to tested hardware/software configurations for a number of onboard Linux computers. 
* :ref:`sitle_setup` for links explaining how to set up a simulated vehicle for Copter, Plane, or Rover.



Installing DroneKit
===================

*DroneKit* can be installed on Linux, Windows and Mac OSX. 

.. _getting_started_installing_dronekit_linux:

Installing DroneKit on Linux
----------------------------

If you are using Ubuntu or Debian Linux you can get most of the *DroneKit* dependencies by running:

.. code:: bash

    sudo apt-get install python-pip python-dev python-numpy python-opencv python-serial python-pyparsing python-wxgtk2.8

	
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

    brew tap homebrew/science
    brew install wxmac wxpython opencv

	
Uninstall *python-dateutil* (OSX and Windows come bundled with a version that is not supported for some dependencies):

.. code:: bash

    sudo pip uninstall python-dateutil

Install DroneKit-Python and its remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_) from the public PyPi repository:

.. code:: bash

    sudo pip install numpy pyparsing
    sudo pip install droneapi
	


Installing DroneKit on Windows
------------------------------

The easiest way to set up DroneKit-Python on Windows is to use the *WinPython* package, which already includes most of the needed dependencies.
You will need remove *python-dateutil* as the installation comes bundled with a version that does not work with some *DroneKit* dependencies.

The steps to install this package and our add-on modules are:

#. Download and run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ (**v2.7**) for your platform (win32 vs win64).
   
   * Run the installer as an administrator (**Right-click** on file, select **Run as Administrator**). 
   * When prompted for the destination location, specify **C:\Program Files (x86)** 
     (the default location is under the Downloads folder).

#. Register the python that came from *WinPython* as the preferred interpreter for your machine:

   Open the folder where you installed WinPython, run *WinPython Control Panel* and choose **Advanced/Register Distribution**.

   .. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

#. Install DroneKit-Python and its remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_) from the public PyPi repository:

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
   * - SITL connected to the vehicle via UDP
     - ``mavproxy.py --master=127.0.0.1:14550``
   * - OSX computer connected to the vehicle via USB
     - ``mavproxy.py --master=/dev/cu.usbmodem1``	 
   * - Windows computer connected to the vehicle via USB
     - ``mavproxy.py --master=/dev/cu.usbmodem1``		 
	    

For other connection options see the `MAVProxy documentation <http://tridge.github.io/MAVProxy/>`_.


.. _loading-dronekit:

Loading DroneKit
================

*DroneKit* is implemented as a *MAVProxy* module (MAVProxy is installed automatically with DroneKit). 
The best way to load the *DroneKit* module into *MAVProxy* is to 
`add it to the startup script <http://tridge.github.io/MAVProxy/mavinit.html>`_ (**mavinit.scr**).

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

This section shows how to run the :ref:`Vehicle State <example-vehicle-state>` example, 
which reads and writes :ref:`vehicle state and parameter <vehicle-information>` information.

.. warning:: 

    This example doesn't take off, but it does arm the motors. Don't run any example indoors on a real vehicle 
    unless you have first removed its propellers.	
	
The steps are:

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this 
   is to clone the **dronekit-python** repository from Github. 
   
   On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/droneapi-python.git

#. Navigate to the **dronekit-python/examples/vehicle_state/** directory.
#. Start MAVProxy :ref:`using the command for your connection <starting-mavproxy>`. 
   Assuming you are connecting to a simulated vehicle:

   .. code-block:: bash

       mavproxy.py --master=127.0.0.1:14550
   
   .. note::

      You should already have set up *MAVProxy* to :ref:`load DroneKit automatically <loading-dronekit>`. 
      If not, manually load the library using:

      .. code-block:: bash

          module load droneapi.module.api
	   
#. Once the *MAVProxy* console is running, start the example by entering: 

   .. code-block:: bash

       api start vehicle_state.py


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


For more information on running the examples (and other apps) see: :ref:`running_examples_top`.	
