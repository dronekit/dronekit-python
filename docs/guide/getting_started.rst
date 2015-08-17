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


.. _get_started_install_dk_windows:

Installing DroneKit on Windows
------------------------------

The easiest way to set up DroneKit-Python on Windows is to use the Windows Installer. 
This is applied over the top of the *MAVProxy* Windows installation and includes all needed 
dependencies and the DroneKit-Python examples.

Download and run the **latest** installers for MAVProxy and DroneKit. Install in the same default location (accepting all prompts):

#. `Latest MAVProxy installer <http://firmware.diydrones.com/Tools/MAVProxy/MAVProxySetup-latest.exe>`_ 
   (`older versions <http://firmware.diydrones.com/Tools/MAVProxy/>`_)    
#. `Latest DroneKit installer <http://dronekit-assets.s3.amazonaws.com/installers/dronekit-windows-latest.exe>`_ 
   (`older versions <http://dronekit-assets.s3-website-us-east-1.amazonaws.com/installers/>`_)

The installer packages DroneKit-Python as an application, which is launched by double-clicking an icon 
in the system GUI. After the *MAVProxy prompt* and *console* have started you can 
:ref:`connect to the vehicle <starting-mavproxy_set_link_when_mavproxy_running>` (instead of setting the
connection when starting *MAVProxy*). You will still need to :ref:`load DroneKit <loading-dronekit>` (not done by the installer 
- see `#267 <https://github.com/dronekit/dronekit-python/issues/267>`_). The examples are copied to :file:`C:\\Program Files (x86)\\MAVProxy\\examples\\`.

.. warning:: 

    The Windows Installer version of *MAVProxy* does not have visibility of the user's default Python environment. Python modules can be added to the environment by copying them into the *MAVProxy* folder (**C:\\Program Files (x86)\\MAVProxy\\**).


.. tip::

    * New versions of the Windows Installers are created with every patch revision. Update regularly for bug fixes and new features!
    * It is also possible to :ref:`set up DroneKit-Python on the command line <dronekit_development_windows>`.


.. _starting-mavproxy:

Starting MAVProxy
=================

Before executing DroneKit scripts you must first start *MAVProxy* and connect to your autopilot (simulated or real). 
The connection to the vehicle can be set up on the command line when starting *MAVProxy* or after MAVProxy is running.

.. tip:: 

    If you're using DroneKit-Python from the Windows installer there is no way to pass command line options to MAVProxy;
    you will have to start MAVProxy by double-clicking its icon and then :ref:`connect to the target vehicle after MAVProxy 
    has started <starting-mavproxy_set_link_when_mavproxy_running>`.

Connecting at startup
---------------------

The table below shows the command lines used to start *MAVProxy* for the respective connection types:

.. list-table:: MAVProxy connection options
   :widths: 10 10
   :header-rows: 1

   * - Connection type
     - MAVProxy command
   * - Linux computer connected to vehicle via USB
     - ``mavproxy.py --master=/dev/ttyUSB0``
   * - Linux computer connected to vehicle via Serial port (RaspberryPi example)
     - ``mavproxy.py --master=/dev/ttyAMA0 --baudrate 57600``
   * - SITL connected to the vehicle via UDP
     - ``mavproxy.py --master=127.0.0.1:14550``
   * - OSX computer connected to vehicle via USB
     - ``mavproxy.py --master=/dev/cu.usbmodem1``
   * - Windows computer connected to vehicle via USB on port "X"
     - ``mavproxy.py --master="comX"``

For other connection options see the `MAVProxy documentation <http://dronecode.github.io/MAVProxy/>`_.

.. _starting-mavproxy_set_link_when_mavproxy_running:

Connecting after startup
------------------------

To connect to the autopilot once *MAVProxy* has already started use ``link add <connection>`` in the *MAVProxy command prompt*, where ``<connection>``
takes the same values as ``master`` in the table above. For example, to set up a connection to SITL running on the local computer at port 14550 do:

.. code:: bash

    link add 127.0.0.1:14550

If you're connecting using a serial port you may need to first set up the baud rate first (the default is 57600). You can change the default baudrate used for 
new connections as shown:

.. code:: bash

    set baudrate 57600    #Set the default baud rate for new connections (do before calling "link add")

See `Link Management <http://tridge.github.io/MAVProxy/link.html>`_ (MAVProxy documentation) for more information.




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

#. Get the DroneKit-Python example source code onto your local machine. 

   The easiest way to do this is to clone the **dronekit-python** repository from Github.   
   On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/droneapi-python.git

   .. tip:: 

       The :ref:`Windows Installation <get_started_install_dk_windows>` copies the example code here: 
       :file:`C:\\Program Files (x86)\\MAVProxy\\examples\\`.

#. Start MAVProxy and :ref:`connect to the vehicle <starting-mavproxy>`. For example:

   * To connect to a simulated vehicle when starting *MAVProxy* (from the command line):

     .. code-block:: bash

         mavproxy.py --master=127.0.0.1:14550
   
   * To connect to a simulated vehicle after starting *MAVProxy* (for example, on Windows):

     .. code-block:: bash

         link add 127.0.0.1:14550

#. You should already have set up *MAVProxy* to :ref:`load DroneKit automatically <loading-dronekit>`. 
   If not, manually load the library using:

   .. code-block:: bash

       module load droneapi.module.api

#. Once the *MAVProxy* console is running, start ``vehicle_state.py`` by entering ``api start`` followed by the 
   full file path of the script. For example: 

   .. code-block:: bash

       api start "C:\Program Files (x86)\MAVProxy\examples\vehicle_state\vehicle_state.py"


   The output should look something like that shown below

   .. code-block:: bash
      :emphasize-lines: 1

       MANUAL> api start "C:\Program Files (x86)\MAVProxy\examples\vehicle_state\vehicle_state.py"
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


For more information on running the examples (and other apps) see :ref:`running_examples_top`.	
