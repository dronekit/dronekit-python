.. _quick-start:

==========
QuickStart
==========

This topic shows the quickest and easiest way to get up and running with DroneKit on Windows, using a pre-built Simulated 
Vehicle (`SITL <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/>`_) hosted in 
a `Vagrant <https://www.vagrantup.com/>`_ virtual machine.

.. tip:: To work with DroneKit on other operating systems and with real vehicles, see :ref:`get-started`.


.. _vagrant-sitl-from-full-image:

Set up the simulated vehicle
============================

1. Get the software for hosting the Simulator onto your computer (Windows, OS-X and Linux are supported):

   * `Download and install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
   * `Download and install Vagrant <https://www.vagrantup.com/downloads.html>`_.

2. Create a new directory where you will run *Vagrant*, and open a command prompt/terminal in it: 

3. Enter the following commands to fetch a *Vagrantfile* for the pre-built SITL image:

   .. code:: bash

       vagrant init 3drobotics/ardupilot-sitl

4. Launch the new image. This takes a long time the *first time* it is run while it downloads the image from the Internet.

   .. code:: bash

       vagrant up

5. SSH into the vagrant instance, and start a vehicle:

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

6. Load a default set of parameters and disable the arming check:

   .. code:: bash
       
       STABILIZE>param load ../Tools/autotest/copter_params.parm
       STABILIZE>param set ARMING_CHECK 0

   .. note:: 
   
       SITL simulates (by default) a vehicle that may not pass the arming check. This change makes the simulated
       vehicle more forgiving, which allows the examples to arm and run. 
	   
       You should never disable the arming check in a script or on a real vehicle.

Install Python and DroneKit
===========================

Install the *WinPython* package and DroneKit on your Windows computer:

5. Run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ for your platform (win32 vs win64)

6. Open the folder where you installed WinPython, run *WinPython Control Panel* and choose **Advanced/Register Distribution** (to register it as the preferred interpreter for your machine):

   .. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

7. Open the *WinPython Command Prompt* and run the following commands to set up DroneKit:

   .. code:: bat

       pip uninstall python-dateutil
       pip install droneapi
       echo module load droneapi.module.api >> %HOMEPATH%\AppData\Local\MAVProxy\mavinit.scr

		
Run an app
==========

This section shows how to run a DroneKit-Python app in `MAVProxy <http://tridge.github.io/MAVProxy/>`_ (*DroneKit* is implemented as a MAVProxy module). For this example, download :download:`vehicle_state.py <../examples/vehicle_state/vehicle_state.py>` or one of our :ref:`other examples <example-toc>`.

	   
7. Navigate to the directory containing the script you want to run (e.g. **vehicle_state.py**).

8. Start *MAVProxy*, specifying the URL where SITL will send UDP packets as shown:

   .. code:: bash

       mavproxy.py --master=127.0.0.1:14550

   *MAVProxy* should connect to the autopilot (SITL). If this worked correctly, you will start seeing status updates like those 
   displayed on the SITL console:
	   
   .. code:: bash

       ...
       MAV> online system 1
       STABILIZE> Mode STABILIZE
       ...


	   
9. Start the *vehicle_state.py* example (as this is in the directory in which you ran *MAVProxy*, no file path is needed):

   .. code:: bash

       STABILIZE> api start vehicle_state.py

   The output should look something like that shown below:

   .. code:: bash
 
       STABILIZE> api start /vagrant/vehicle_state.py
       STABILIZE> Mode: VehicleMode:STABILIZE
       Location: Location:lat=-35.363261,lon=149.16523,alt=0.0,is_relative=False
       ...
       APIThread-0 exiting...

That's it! You now have a DroneKit-Python environment you can use for testing your scripts against a simulated vehicle.

.. tip::

    :ref:`get-started` explains how to use DroneKit on Windows in more detail, including how to :ref:`watch the 
    movement of your vehicle on a map <viewing_uav_on_map>`. In addition, it explains how to use DroneKit on Linux and Mac OSX,  
    and with real vehicles.


