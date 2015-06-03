.. _dronekit_development_linux:

========================================================
Setting up DroneKit-Python for Development on Linux
========================================================

This topic shows how to set up development environment for DroneKit-Python on a Linux machine. The 
instructions assume taht you have already set up SITL as described in the wiki article 
`Setting up SITL on Linux <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/setting-up-sitl-on-linux/>`_.

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
	   
#. Load a default set of parameters and disable the arming check:

   .. code:: bash
       
       STABILIZE>param load ../Tools/autotest/copter_params.parm
       STABILIZE>param set ARMING_CHECK 0

	   
That's it - the prompt is now set up for running DroneKit scripts.  You can run your test code 
or an example (in this case **vehicle_state.py**) as shown:

.. code:: bash

    STABILIZE>api start ../dronekit-python/example/vehicle_state/vehicle_state.py


.. note:: 

    Remember that script locations have to be specified relative to wherever *MAVProxy* is started. 
    In this case, it is started in the vehicle directory (e.g. **~/ardupilot/ArduCopter**).

