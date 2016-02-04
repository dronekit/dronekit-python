.. _installing_dronekit:

===================
Installing DroneKit
===================

DroneKit-Python can be installed on a Linux, Mac OSX, or Windows computer that 
has *Python 2.7* and can install Python packages from the Internet.

It is installed from **pip** on all platforms:

.. code-block:: bash

    pip install dronekit


**Installation notes:**

* Mac and Linux require you prefix the command with ``sudo``.
    
  .. code-block:: bash

      sudo pip install dronekit
      
* On Linux you may need to first install **pip** and **python-dev**:
    
  .. code-block:: bash

      sudo apt-get install python-pip python-dev
      
  Alternatively, the *easy_install* tool provides another way to install pip:
  
  .. code-block:: bash

      sudo easy_install pip
      
* :doc:`companion-computers` are likely to run on stripped down versions of Linux. Ensure
  you use a variant that supports Python 2.7 and can install Python packages from the Internet.
* Windows does not come with Python by default, but there are 
  `many distributions available <https://www.python.org/download/alternatives/>`_. 
  We have tested against:
    
  * `WinPython 2.7 64bit <http://sourceforge.net/projects/winpython/files/WinPython_2.7/>`_ (see 
    `these instructions for installation and registration <https://github.com/winpython/winpython/wiki/Installation>`_). This is the most tested version.    
  * `ActiveState ActivePython 2.7 <http://www.activestate.com/activepython/downloads>`_.
* Python 3 is not supported.
