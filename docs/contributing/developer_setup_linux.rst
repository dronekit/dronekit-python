.. _dronekit_development_linux:

===================================
Building DroneKit-Python on Linux
===================================

The setup for *developing* DroneKit-Python on Linux is almost the same as for *using* 
DroneKit-Python. We therefore recommend that you start by following the instructions in 
:ref:`installing_dronekit`. 

When you've got DroneKit and a vehicle (simulated or real) communicating, you can 
then build and install your own fork of DroneKit, as discussed below.


Fetch and build DroneKit source
===============================

#. Fork the `dronekit-python <https://github.com/dronekit/dronekit-python>`_ project on Github.

#. Run the following commands to clone and build DroneKit (in the directory of your choice):
  
   .. code:: bash

       git clone https://github.com/<your_fork_of_dronekit>/dronekit-python.git
       cd ./dronekit-python
       sudo python setup.py build
       sudo python setup.py install

	   
Updating DroneKit
=================

Navigate to your local git fork, pull the latest version, and rebuild/install:

.. code:: bash

    cd ./<path-to-your-dronekit-fork>/dronekit-python
    git pull
    sudo python setup.py build
    sudo python setup.py install


