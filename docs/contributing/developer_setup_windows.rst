.. _dronekit_development_windows:

===================================
Building DroneKit-Python on Windows
===================================

This article shows how to set up an environment for *developing* DroneKit-Python on Windows. 

.. tip::

    If you just want to *use* DroneKit-Python on Windows then easiest way to get started is to use the 
    :ref:`Windows Installer <_get_started_install_dk_windows>`.  The installer is rebuilt with every patch
    release, so you can always be up to date with the latest features and bug fixes.


Install DroneKit using WinPython command line
=============================================

First set up a command line DroneKit-Python installation using *WinPython*. This Python distribution already includes most of the needed dependencies (though you will need remove *python-dateutil* as the installation comes bundled with a version that does not work with *DroneKit*).

The steps to install this package and the most important add-on modules are:

#. Download and run the correct `WinPython installer <http://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.6.4/>`_ (**v2.7**) for your platform (win32 vs win64).
   
   * Run the installer as an administrator (**Right-click** on file, select **Run as Administrator**). 
   * When prompted for the destination location, specify **C:\Program Files (x86)** 
     (the default location is under the **Downloads** folder).

#. Register the Python that came from *WinPython* as the preferred interpreter for your machine:

   Open the folder where you installed WinPython, run *WinPython Control Panel* and choose **Advanced/Register Distribution**.

   .. image:: http://dev.ardupilot.com/wp-content/uploads/sites/6/2014/03/Screenshot-from-2014-09-03-083816.png

#. Install DroneKit-Python and its remaining dependencies (including `MAVProxy <http://tridge.github.io/MAVProxy/>`_) from the public PyPi repository:

   Open the *WinPython Command Prompt* and run the following two commands:

   .. code:: bash

	    pip uninstall python-dateutil
	    pip install droneapi

The dependencies above are all that are required to build DroneKit-Python and the *MAVProxy command line* (i.e. the minimum needed for testing). 
If you also want the *MAVProxy console* and map install:
	
#. OpenCV

   * `Download and install OpenCV version 2.4 for Windows <http://opencv.org/downloads.html>`_ (this can be extracted anywhere)
   *  Copy/paste the file :file:`cv2.pyd` from :file:`OpenCV\\build\\python\\2.7\\x64\\` to :file:`site_packages` 
      on your Python installation (e.g. :file:`\\python-2.7.6.amd64\\Lib\\site-packages`).
#. WxPython 

   * `Download and install WxPython <http://www.wxpython.org/download.php>`_. Make sure the target
     path is your WinPython installation.
#. Console

   * Open the WinPython command prompt and enter:
   
     .. code:: bash

         pip install console



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


