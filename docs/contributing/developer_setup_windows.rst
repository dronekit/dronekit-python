.. _dronekit_development_windows:

===================================
Building DroneKit-Python on Windows
===================================

This article shows how to set up an environment for *developing* DroneKit-Python on Windows. 


Install DroneKit using WinPython command line
=============================================


First set up a command line DroneKit-Python installation. We recommend *WinPython* or *ActivePython*, as discussed in :ref:`installing_dronekit`.



Fetch and build DroneKit source
===============================

#. Fork the `dronekit-python <https://github.com/dronekit/dronekit-python>`_ project on Github.

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


