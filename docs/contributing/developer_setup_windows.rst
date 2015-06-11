.. _dronekit_development_windows:

===================================
Building DroneKit-Python on Windows
===================================

The setup for *developing* DroneKit-Python on Windows is almost the same as for *using* 
DroneKit-Python. We therefore recommend that you start by following the instructions in the :ref:`get-started`. 

When you've got DroneKit and a vehicle (simulated or real) communicating, you can 
then build and install your own fork of DroneKit, as discussed below.


Fetch and build DroneKit source
===============================

#. Fork the `dronekit-python <https://github.com/diydrones/dronekit-python>`_ project on Github.

#. Open the *WinPython Command Prompt*. Run the following commands to clone and build DroneKit (in the directory of your choice):
  
   .. code:: bash

       git clone https://github.com/<your_fork_of_dronekit>/dronekit-python.git
       cd dronekit-python
       python setup.py build
       python setup.py install


	   
Updating DroneKit
=================

Navigate to your local git fork, pull the latest version, and rebuild/install:

.. code:: bash

    cd <path-to-your-dronekit-fork>/dronekit-python
    git pull
    python setup.py build
    python setup.py install


