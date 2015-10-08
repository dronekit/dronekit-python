.. _migrating_dkpy2_0:

=====================
Migrating to DKPY 2.0
=====================

DroneKit-Python 2.0 has undergone a significant *architectural* evolution when compared to version 1.x (the library changed from a MAVProxy extension
to a standalone Python module). The API itself remains largely compatible, with the most important difference being that you
now need to specify the vehicle target address inside the script.

The sections below outline the main migration areas.


Installation
============

DKPY 2.0 is installed from `pip` on all platforms - see :ref:`get-started` for more information.

.. note::

    The DroneKit-Python Windows installer is no longer needed. Installation is generally simpler 
    than on DK 1.x because MAVProxy is not a dependency.


Launching scripts
=================

DroneKit-Python 2.0 apps are run from an ordinary Python command prompt. For example:

.. code:: bash

    some_python_script.py    # or `python some_python_script.py`

.. note::

    This contrasts with DKPY 1.x scripts, which were run from within MAVProxy using the command:
    
    .. code:: bash
    
        api start some_python_script.py
    

Code changes
============

This section outlines the changes you will need to make to your DroneKit-Python scripts.

Connecting to a vehicle
-----------------------

You must specify the target vehicle address in your script (in DKPY 1.x this was done when you launched MAVProxy).

The code fragment below shows how you import the :py:func:`connect() <dronekit.lib.connect>` method and use it to return a 
connected :py:class:`Vehicle <dronekit.lib.Vehicle>` object. The address string passed to ``connect()`` takes the same 
values as were passed to MAVProxy when setting up a connection in DKPY 1.x (in this case, a SITL instance running on the same computer). 

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle
    vehicle = connect('127.0.0.1:14550')
    
    # Wait for attributes to accumulate.
    time.sleep(5)

The thread is normally suspended for a few seconds after connecting. This allows *MAVLink* messages to arrive from the connected vehicle 
and populate the ``Vehicle`` attributes (before they are read). The vehicle can then be used in exactly the same way as in DKPY 1.x. 

.. note::

    The above code replaces DKPY 1.x code to get the Vehicle (similar to the example below):
 
    .. code:: python

        # Get an instance of the API endpoint
        api = local_connect()
        # Get the connected vehicle (currently only one vehicle can be returned).
        vehicle = api.get_vehicles()[0] 
  

   
.. todo:: Above link to the connect method in API ref - make sure connect() is documented.


Exit status checks
------------------

Remove code that checks the ``api.exit`` status (note that the ``api.exit`` call below is commented out). DroneKit no 
longer runs in *MAVProxy* so scripts don't need to monitor and act on external thread shutdown commands.

.. code:: python

    while not vehicle.armed   # and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)

.. note::

    In fact you should delete all references to ``APIConnection`` class and its methods (``get_vehicles()``, ``exit()`` and ``stop()``). 


.. todo:: Find out how to check the connection status is still valid. That would go in separate section.


        
Command line arguments
----------------------

Remove any code that uses the ``local_arguments`` array to get script-local command line arguments (via MAVProxy).

From DKPY 2.0 command line arguments are passed to ``sys.argv`` as with any other script. The examples use the 
`argparse <https://docs.python.org/3/library/argparse.html>`_ module for argument parsing, but you can
use whatever method you like.

.. note::

    In DKPY 1.x the script's ``sys.argv`` values were the values passed to MAVProxy when it was
    started. To access arguments passed to the script from *MAVProxy you used the ``local_arguments`` array. 
    For example if you started a script as shown below:

    .. code:: bash

        api start my_script.py 101

    Then you would read the integer in your code using

    .. code:: python

        my_argument = int(local_arguments[0])

        
.. todo:: This addition closes https://github.com/dronekit/dronekit-python/issues/13


