.. _dronekit_development_vagrant:

========================================================
Setting up DroneKit-Python for Development using Vagrant
========================================================

This topic shows how to set up an environment for developing DroneKit-Python using Vagrant (on Windows/Mac OSX).

.. note:: 

   Setting up an environment to develop DroneKit-Python is much like setting up an environment to develop *using* DroneKit-Python.
   The main difference is that here we show you how to build and install DroneKit from source (rather than using a pre-built version).

First-time setup
================

This section shows how to install DroneKit-Python into the `3drobotics/ardupilot-sitl <https://atlas.hashicorp.com/3drobotics/boxes/ardupilot-sitl>`_ vagrant image used for the :ref:`QuickStart <quick-start>` and run DroneKit scripts from **SITL's MAVProxy prompt**.

.. note:: 

    Using SITL's prompt is the easiest way to set up a development environment, but has the limitation that DroneKit can 
    *only* communicate with SITL. If you want to set up DroneKit to talk to a real device then you need to 
    set up a separate MAVProxy and DroneKit instance.
	
The steps are:

#. Get the software for hosting the Simulator onto your computer (Windows, OS-X and Linux are supported):

   * `Download and install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
   * `Download and install Vagrant <https://www.vagrantup.com/downloads.html>`_.

#. Create a new directory where you will run *Vagrant*, and open a command prompt/terminal in it.

#. Enter the following commands to fetch a *Vagrantfile* for the pre-built SITL image:

   .. code:: bash

       vagrant init 3drobotics/ardupilot-sitl

#. Launch the new image. This takes a long time the *first time* it is run while it downloads the image from the Internet.

   .. code:: bash

       vagrant up


#. SSH into the vagrant instance and open the **src** directory. Then clone your fork of DroneKit-Python:

   .. code:: bash

       vagrant ssh
       cd src
       git clone https://github.com/<your_fork_of_dronekit_python>/dronekit-python.git


#. Navigate into the DroneKit source and build/install it:

   .. code:: bash

       cd ./dronekit-python
       sudo python setup.py build
       sudo python setup.py install

#. Set :program:`MAVProxy` to load DroneKit on startup:

   .. code:: bash

       echo "module load droneapi.module.api" >> ~/.mavinit.scr

#. Now navigate back to the user root and start a vehicle:

   .. code:: bash

       cd
       ./sitl.sh

   When prompted, enter your desired vehicle (e.g. "copter") to build/start SITL.
   Once complete, you will see a MAVProxy prompt displaying periodic vehicle-status updates: 

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

    STABILIZE>api start ../../dronekit-python/example/vehicle_state/vehicle_state.py


.. note:: 

    Remember that script locations have to be specified relative to wherever *MAVProxy* is started. 
    In this case, it is started in the vehicle directory (e.g. **~/ardupilot/ArduCopter**).



Restarting the development environment
======================================

To restart the development environment, first navigate to your SITL/Vagrant directory, 
bring up the vagrant instance, and then SSH into it:

.. code:: bash

    vagrant up
    vagrant ssh	
	
To start the simulator, enter the following into the SSH session:

.. code:: bash

    ./sitl.sh

Then select your target vehicle (e.g. "copter").

Once the simulator is running you will see a :program:`MAVProxy` prompt displaying periodic vehicle-status updates:

.. code:: bash

    Ready to FLY  ublox Received 454 parameters
    fence breach
    ...

   
That's it. You can run test/example code as shown in the previous section.

.. todo:: 

    When https://github.com/mrpollo/sitl-vagrant-recipe/issues/1 is fixed we will be 
    able to pass the -w parameter as shown in the linux docs. Update then!


Updating DroneKit
=================

First start vagrant and open an SSH session (in your vagrant directory):

.. code:: bash

    vagrant up
    vagrant ssh	

Then navigate to the source, pull the latest version, and rebuild/install 

.. code:: bash

    cd src/dronekit-python
    git pull
    sudo python setup.py build
    sudo python setup.py install

After building you can restart the simulator as shown in the preceding section.
