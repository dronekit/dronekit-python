.. _dronekit_development_vagrant:

========================================================
Setting up DroneKit-Python for Development using Vagrant
========================================================

One of the easiest ways to set up a DroneKit-Python environment for development/testing it is to add it to the `3drobotics/ardupilot-sitl <https://atlas.hashicorp.com/3drobotics/boxes/ardupilot-sitl>`_ vagrant image used for the :ref:`QuickStart <quick-start>`:

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


#. SSH into the vagrant instance and open the **src** directory. Then get the branch you want to test (in this case we’ll just clone the master repo)

   .. code:: bash

       vagrant ssh
       cd src
       git clone https://github.com/diydrones/dronekit-python.git


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

