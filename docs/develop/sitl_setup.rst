.. _sitl_setup:

=====================================
Setting up a Simulated Vehicle (SITL)
=====================================

The `SITL (software in the loop) <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/>`_ 
simulator allows you to create and test DroneKit-Python apps without a real vehicle (and from the comfort of 
your own developer desktop!)

SITL runs natively on Linux and Windows, or within a virtual machine on Mac OSX, Linux or Windows. It can be 
installed on the same computer as DroneKit, or on another computer on the same network.

The sections below explain how set up SITL for the different operating systems, 
and how you can set up SITL to connect to Mission Planner and DroneKit at the same time.

Setting up SITL on Linux
========================

Build and install SITL on Linux using the instructions in: 
`Setting up SITL on Linux <http://dev.ardupilot.com/wiki/setting-up-sitl-on-linux/>`_ (ArduPilot wiki)


Setting up SITL on Windows
==========================

Build and install SITL on Windows using the instructions in:  
`Setting up SITL on Windows <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/sitl-native-on-windows/>`_ 
(ArduPilot wiki)


.. _vagrant-sitl-from-full-image:

Set up SITL using Vagrant (MacOS)
=================================

This section shows how to bring up a pre-built SITL instance hosted in a `Vagrant <https://www.vagrantup.com/>`_ 
virtual machine. This approach should be used if you need to run SITL on MacOS. It can also be used for Windows 
and Linux (though we recommend the native installations linked above).

.. warning:: 

       The Vagrant virtual machine is "headless" (has no UI) and so SITL cannot display the MAVProxy map and console. 
       You can still see and send messages in the SITL Command Prompt.
     

#. Get the software for hosting the Simulator onto your computer (Windows, OS-X and Linux are supported):

   * `Download and install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
   * `Download and install Vagrant <https://www.vagrantup.com/downloads.html>`_.

#. Install SSH (Windows only - SSH is present by default on Linux/Mac OSX)

   * Download and install `Git for Windows <https://git-scm.com/download/win>`_ (or another client that comes with SSH).
     After installing you can locate the file using the command ``C:\where ssh`` (normally it is installed to **C:\Program Files (x86)\Git\bin\ssh.exe**
   * Add the ssh.exe location to the *Path* (**System Properties | Advanced tab | Environment Variables | Path**)

#. Create a new directory where you will run *Vagrant*, and open a command prompt/terminal in it: 

#. Enter the following commands to fetch a *Vagrantfile* for the pre-built SITL image:

   .. code:: bash

       vagrant init 3drobotics/ardupilot-sitl

#. Launch the new image. This takes a long time the *first time* it is run while it downloads the image from the Internet.

   .. code:: bash

       vagrant up

#. SSH into the vagrant instance, and start a vehicle:

   .. code:: bash

       vagrant ssh
       ./sitl.sh
   
   When prompted, enter your desired vehicle (e.g. "copter") to build/start SITL.
   Once complete, you will see a MAVProxy prompt displaying periodic vehicle-status updates: 

   .. code:: bash

       Ready to FLY  ublox Received 454 parameters
       fence breach
       APM: PreArm: RC not calibrated
       ...

.. _disable-arming-checks:

#. Load a default set of parameters and disable the arming check:

   .. code:: bash
       
       STABILIZE>param load ../Tools/autotest/copter_params.parm
       STABILIZE>param set ARMING_CHECK 0

   .. note:: 
   
       SITL simulates (by default) a vehicle that may not pass the arming check. This change makes the simulated
       vehicle more forgiving, which allows the examples to arm and run. 
	   
       You should never disable the arming check in a script or on a real vehicle.


.. _viewing_uav_on_map:

Connecting an additional Ground Station
=======================================

This section explains how you can connect multiple ground stations to a running SITL instance in addition to your DroneKit MAVProxy link.

To do this you first need to get SITL to output to an additional UDP port of your computer:

* Find the network IP address of your computer (On Windows you can get this by running *ipconfig* in the *Windows Command Prompt*). 
* In the *SITL Command Prompt*, add the IP address of the GCS computer (e.g. 192.168.2.10) and an unused port (e.g. 145502) as an output:
  
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

