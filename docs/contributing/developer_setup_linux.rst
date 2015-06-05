.. _dronekit_development_linux:

===================================================
Setting up DroneKit-Python for Development on Linux
===================================================

This topic shows how to set up an environment for developing DroneKit-Python (on a Linux machine).

The instructions assume that you have already set up SITL as described in the wiki article
`Setting up SITL on Linux <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/setting-up-sitl-on-linux/>`_.

.. note:: 

   Setting up an environment to develop DroneKit-Python is much like setting up an environment to develop *using* DroneKit-Python.
   The main difference is that here we show you how to build and install DroneKit from source (rather than using a pre-built version).

First-time setup
================

These instructions explain how set up SITL and DroneKit-Python on a Linux machine, and run it for the first time:

.. note:: 

    The approach described here uses **SITL's MAVProxy prompt** to run MAVProxy. This is the easiest way to set up a development environment, but has the limitation that DroneKit can *only* communicate with SITL. If you want to set up DroneKit to talk to a real device then you need to set up a separate MAVProxy and DroneKit instance.

To get up and running, do the following:

#. `Set up SITL on Linux <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/setting-up-sitl-on-linux/>`_.
   If running SITL, exit to the terminal (Ctrl+X)

#. Clone your fork of the DroneKit-Python source:

   .. code:: bash

       git clone https://github.com/<your_username>/dronekit-python

   
#. Navigate into the **/dronekit-python** directory and build/install it:

   .. code:: bash

       cd ./dronekit-python
       sudo python setup.py build
       sudo python setup.py install
	   
#. Set :program:`MAVProxy` to load DroneKit on startup:

   .. code:: bash

       echo "module load droneapi.module.api" >> ~/.mavinit.scr   

#. Navigate to the target vehicle directory (e.g. **/ardupilot/ArduCopter**) and start the simulator. 

   .. note:: The "cd" path below assumes that you cloned **ardupilot** into the home directory.
	   
   .. code:: bash

       cd ~/ardupilot/ArduCopter
       ./sim_vehicle.sh -w

   Once complete, you will see a :program:`MAVProxy` prompt displaying periodic vehicle-status updates:

   .. code:: bash

       Ready to FLY  ublox Received 454 parameters
       fence breach
       ...
	   
#. Disable the arming check:

   .. code:: bash
       
       STABILIZE>param set ARMING_CHECK 0

	   
That's it - the prompt is now set up for running DroneKit scripts.  You can run your test code 
or an example (in this case **vehicle_state.py**) as shown:

.. code:: bash

    STABILIZE>api start ../dronekit-python/example/vehicle_state/vehicle_state.py


.. note:: 

    Remember that script locations have to be specified relative to wherever *MAVProxy* is started. 
    In this case, it is started in the vehicle directory (e.g. **~/ardupilot/ArduCopter**).


Restarting the development environment
======================================

All you have to do to restart SITL/DroneKit is navigate to the target vehicle directory 
(e.g. **/ardupilot/ArduCopter**) and start the simulator:

.. code:: bash

    cd ~/ardupilot/ArduCopter
    ./sim_vehicle.sh
	
.. tip:: 

    The command above will start the simulator using the same configuration/settings as the previous session.
    If you want to start using the original/default stettings, start the simulator using ``./sim_vehicle.sh -w``.

Once complete, you will see a :program:`MAVProxy` prompt displaying periodic vehicle-status updates:

.. code:: bash

    Ready to FLY  ublox Received 454 parameters
    fence breach
    ...

	   
That's it - the prompt is now set up for running DroneKit scripts.  You can run your test code 
or an example as shown in the previous section.



Updating DroneKit
=================

Updating DroneKit is also easy. Simply navigate into the **/dronekit-python** directory, 
update the branch from git, and rebuild/install:

.. code:: bash

    cd ./dronekit-python
    git pull
    sudo python setup.py build
    sudo python setup.py install

After building you can restart the simulator as shown in the preceding section.