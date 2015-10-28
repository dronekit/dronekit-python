.. _get-started:

===============
Getting Started
===============

DroneKit-Python apps are typically run on Linux-based *companion computers* that travel 
on the vehicle and communicate with the autopilot via a serial port. However, during development it is usually easier to 
prototype apps on a standard Mac, Windows, or Linux computer using a *simulated* autopilot. 


This topic explains how to set up and run DroneKit-Python on the different host operating systems
and then create and run a basic DroneKit app. 



Setting up the vehicle/autopilot
================================

For information on how to set up a vehicle (real and simulated) see:

* :ref:`supported-companion-computers` for links to tested hardware/software configurations for a number of onboard Linux computers. 
* :ref:`sitl_setup` for links explaining how to set up a simulated vehicle for Copter, Plane, or Rover.



Installing DroneKit
===================

*DroneKit* can be installed on Linux, Windows and Mac OSX.


.. _getting_started_installing_dronekit_linux:

Installing DroneKit on Linux
----------------------------

If you are using Ubuntu or Debian Linux you can get most of the *DroneKit* dependencies by running:

.. code:: bash

    sudo apt-get install python-pip python-dev


The remaining dependencies are installed when you get DroneKit-Python from the public PyPi repository:

.. code:: bash

    sudo pip install dronekit



.. tip:: 

    If you are planning to run *DroneKit* on a :ref:`companion computer <supported-companion-computers>`, make sure that the 
    computer runs a variant of Linux that support Python and can install Python packages from the internet.


Installing DroneKit on Mac OSX
------------------------------

Install DroneKit-Python and its dependencies from the public PyPi repository:

.. code:: bash

    sudo pip install dronekit
    


.. _get_started_install_dk_windows:

Installing DroneKit on Windows
------------------------------

Set up a command line DroneKit-Python installation using *WinPython* (this Python distribution already includes most of the needed dependencies).


#. Download and run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ (**v2.7**) for your platform (win32 vs win64).
   
   * Run the installer as an administrator (**Right-click** on file, select **Run as Administrator**). 
   * When prompted for the destination location, specify **C:\\Program Files (x86)** 
     (the default location is under the **Downloads** folder).

#. Register the Python that came from *WinPython* as the preferred interpreter for your machine:

   Open the folder where you installed WinPython, run *WinPython Control Panel* and choose **Advanced/Register Distribution**.

   .. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

#. Install DroneKit-Python and its remaining dependencies from the public PyPi repository:

   Open the *WinPython Command Prompt* and run the following command:

   .. code:: bash

        pip install dronekit

        
        
.. _get_started_connect_string:

.. _get_started_connecting:

Connecting to a Vehicle
=======================

The connection to the vehicle is set up within the DroneKit script. Scripts import and call the :py:func:`connect()` method. 
After connecting this returns a :py:class:`Vehicle <dronekit.lib.Vehicle>` object from which you can get/set parameters 
and attributes, and control vehicle movement.

.. code:: python

    from dronekit import connect
    
    # Connect to UDP endpoint.
    vehicle = connect('127.0.0.1:14550', await_params=True)
    
.. note:: 

    Calling ``connect()`` with ``await_params=True`` (as shown above) ensures that the method will not return until 
    :py:attr:`Vehicle.parameters <dronekit.lib.Vehicle.parameters>` is fully populated with values from the vehicle. 
    Vehicle *attributes* are populated in parallel but are not guaranteed to have values when ``connect()`` completes 
    (an attribute will have value ``None`` if a corresponding MAVLink message has not been received - for example, 
    if the attribute is not supported by the vehicle).

The example above connects to the udp address ``127.0.0.1:14550``. The table below shows addresses to use some of 
the more common connection types:



.. list-table:: Connection string options
   :widths: 10 10
   :header-rows: 1

   * - Connection type
     - Connection string
   * - Linux computer connected to the vehicle via USB
     - ``/dev/ttyUSB0``
   * - Linux computer connected to the vehicle via Serial port (RaspberryPi example)
     - ``/dev/ttyAMA0,57600``
   * - SITL connected to the vehicle via UDP
     - ``127.0.0.1:14550``
   * - OSX computer connected to the vehicle via USB
     - ``dev/cu.usbmodem1``
   * - Windows computer connected to the vehicle via USB (in this case on COM14)
     - ``com14``

.. tip::

    The strings above are the same as you would use if connecting with MAVProxy. For other options see the 
    `MAVProxy documentation <http://dronecode.github.io/MAVProxy/html/getting_started/starting.html#master>`_.

    
You can start this simple script in the same way you would start any other standalone Python script. 

.. code-block:: bash

    python your_dronekit_script.py



.. todo:: Connect method here needs to link to the function, but it isn't exported yet. Fix that once the API tidied.




.. _getting-started-running_examples:

Running an app/example
======================

This SDK has :ref:`numerous examples <example-toc>`. We recommend you start with :ref:`example-vehicle-state`, 
which reads and writes :ref:`vehicle state and parameter <vehicle-information>` information. 

For general information on running the examples (and other apps) see :ref:`running_examples_top`.
