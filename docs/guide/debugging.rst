.. _debugging:

=========
Debugging  
=========

DroneKit-Python apps can be debugged in the same way as any other standalone Python scripts.
The sections below outline a few methods. 



pdb - The Python Debugger
=========================

The `Python Debugger - pdb <https://docs.python.org/2/library/pdb.html>`_ can be used to debug *DroneKit-Python* apps.

The command below can be used to run a script in debug mode:

.. code-block:: bash

    python -m pdb my_dronekit_script.py
    
You can also instrument your code to invoke the debugger at a certain point. To do this  
add ``set-trace()`` at the point where you want to break execution:

.. code-block:: python
    :emphasize-lines: 4

    # Connect to the Vehicle on udp at 127.0.0.1:14550
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

    import pdb; pdb.set_trace()
    print "Global Location: %s" % vehicle.location.global_frame


The available `debugger commands are listed here <https://docs.python.org/2/library/pdb.html#debugger-commands>`_. 

pudb - A full-screen, console-based Python debugger
===================================================

If you prefer a IDE like debug you can use `pudb - A full-screen, console-based Python debugger <https://pypi.python.org/pypi/pudb>`_. 

.. code-block:: python
    :emphasize-lines: 4

    pip install pudb


To start debugging, simply insert:

.. code-block:: python
    :emphasize-lines: 4

    from pudb import set_trace; set_trace()

Insert either of these snippets into the piece of code you want to debug, or run the entire script with:

.. code-block:: python
    :emphasize-lines: 4

    pudb my-script.py


Print/log statements
====================

The simplest and most common method of debugging is to manually add debug/print statements to the source.

.. code-block:: python
    :emphasize-lines: 4

    # Connect to the Vehicle on udp at 127.0.0.1:14550
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

    # print out debug information
    print "Global Location: %s" % vehicle.location.global_frame

In addition to printing DroneKit variables, Python provides numerous inbuilt and add-on modules/methods 
for inspecting code (e.g. `dir() <https://docs.python.org/2/library/functions.html#dir>`_, `traceback <https://docs.python.org/2/library/traceback.html>`_, etc.)


Other IDEs/debuggers
====================

There is no reason you should not be able to straightforwardly use other popular Python IDEs including IDLE and Eclipse.




