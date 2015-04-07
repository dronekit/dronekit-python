===============
Getting Started
===============

On-board apps for drones typically run on a Linux-based "companion computer" that communicates with the autopilot via a serial port.  However, you may find it easier to first prototype your app on a standard Mac, Windows, or Linux
computer using a simulated autopilot, a process called "Software in the Loop Simulation" (SITL). This document will show you how to do both of these.


Supported Companion Computers
=============================


RaspberryPi
-----------

* `Communicating with Raspberry Pi via MAVLink <http://dev.ardupilot.com/wiki/companion-computers/raspberry-pi-via-mavlink/>`_
* `Making a Mavlink WiFi bridge using the Raspberry Pi <http://dev.ardupilot.com/wiki/companion-computers/raspberry-pi-via-mavlink/making-a-mavlink-wifi-bridge-using-the-raspberry-pi/>`_

Intel Edison
------------

* `Edison for drones <http://dev.ardupilot.com/wiki/companion-computers/edison-for-drones/>`_

BeagleBoneBlack
---------------

* `BeaglePilot <http://dev.ardupilot.com/wiki/companion-computers/beaglepilot/>`_

Odroid
------
* `Communicating with ODroid via MAVLink <http://dev.ardupilot.com/wiki/companion-computers/odroid-via-mavlink/>`_
* `ODroid Wifi Access Point for sharing files via Samba <http://dev.ardupilot.com/wiki/companion-computers/odroid-via-mavlink/odroid-wifi-access-point-for-sharing-files-via-samba/>`_


Installing DroneKit
===================

If you are using a virtual vehicle to prototype, it is recommended that you install DroneKit on that virtual environment where you are running SITL.

If you are planning to run DroneKit on an onboard computer, make sure that the onboard computer run a variant of Linux that support Python and can install Python packages from the internet.


Linux dependencies
------------------

If you are running Ubuntu or Debian Linux you can get all the DroneKit dependencies by running:

::

    sudo apt-get install python-pip python-numpy python-opencv python-serial python-pyparsing python-wxgtk2.8


OSX dependencies
----------------

If you're on Mac OSX, you can use `Homebrew <http://brew.sh/>`_ to install WXMac.

::

    brew install wxmac

Install the following python libraries

::

    pip install numpy pyparsing

On OSX you need to uninstall python-dateutil since osx comes bundled with a version that is not supported for some dependencies

::

    pip uninstall python-dateutil


Windows dependencies
--------------------

The windows installation is a little more involved, but not too hard.

You could install the various python libraries by hand, but we think that it is easier to use the WinPython package, the steps to install this package and our add-on modules are:

1. Run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ for your platform (win32 vs win64)

2. Register the python that came from *WinPython* as the preferred interpreter for your machine:

Open the folder where you installed WinPython, run "*WinPython Control Panel*" and choose “*Advanced/Register Distribution*“.

.. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

3. Run "*WinPython Command Prompt*" and run the following two commands:

::

	pip uninstall python-dateutil
	pip install droneapi

Install MAVProxy
----------------

When developing new DroneKit Python code the easiest approach is to run it inside of MAVProxy, a lightweight CLI tool to send MAVLink messages. Learn more about MAVProxy `here <http://tridge.github.io/MAVProxy/>`_.

Install MAVProxy with the following command:

::

    sudo pip install MAVProxy


Set up DroneKit
---------------

The DroneKit library is available on the public pypi repository. You can use the PyPi tool to install.

::

    pip install droneapi


Set up a simulated vehicle
==========================
The best way to prototype apps for drones is to use a simulated vehicle. APM provides a Software-In-The-Loop (SITL) environment, which simulates a copter or plane, in Linux.

If you want to test your app in real life, you should also grab a ready to fly copter from the  `3D Robotics Store <http://store.3drobotics.com>`_.



Dependencies
------------

If you are using Mac OSX or Windows, you need to set up a virtual Linux machine to run SITL.

A popular virtual machine manager for running SITL is `Virtual Box <https://www.virtualbox.org/>`_. A virtual machine running Ubuntu Linux 13.04 or later works great.


Set up SITL on Linux
--------------------

Please see `instructions here <http://dev.ardupilot.com/wiki/setting-up-sitl-on-linux/>`_ to set up SITL on Ubuntu.

Once you have the simulated vehicle running, enter the following commands. (You only have to do this once)

1. Load a default set of parameters
2. Disable the arming check

::

    STABILIZE>param load ../Tools/autotest/copter_params.parm
    STABILIZE>param set ARMING_CHECK 0

