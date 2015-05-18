.. _debugging:

=========
Debugging  
=========

DroneKit-Python apps are run in the context of a MAVProxy console.  This can make debugging 
more challenging:

* MAVLink updates are continually displayed in the console and may be interspersed with (or even
  mixed into) output from the script or a console debug session. This can make it hard to run a debug session
  or read debug output.
* It is not possible to directly launch a script in a debug session. Instead debugging must be
  either started from within the script or the debugger must be attached to the running script.

That said, it is possible to effectively debug DroneKit apps. The main methods are discussed below.

.. note:: 

    We are actively working to improve debugging on DroneKit-Python! You can track progress and suggestions
    on `Github Issue #118 <https://github.com/diydrones/dronekit-python/issues/118>`_.


Print/log statements
====================

The simplest and most common method of debugging is to manually add debug/print statements to the source.

.. code-block:: python
    :emphasize-lines: 6

    # Get the vehicle
    api = local_connect()
    vehicle = api.get_vehicles()[0]

    # print out debug information
    print "Location: %s" % vehicle.location

In addition to printing DroneKit variables, Python provides numerous inbuilt and add-on modules/methods 
for inspecting code (e.g. `dir() <https://docs.python.org/2/library/functions.html#dir>`_, `traceback <https://docs.python.org/2/library/traceback.html>`_, etc.)


pdb - The Python Debugger
=========================

The `Python Debugger - pdb <https://docs.python.org/2/library/pdb.html>`_ can be used to debug *DroneKit-Python* apps.
To start debugging, add ``set-trace()`` at the point where you want to break execution (as shown below):


.. code-block:: python
    :emphasize-lines: 5
	
    # Get the vehicle
    api = local_connect()
    vehicle = api.get_vehicles()[0]
	
    import pdb; pdb.set_trace()
    print "Location: %s" % v.location

When you run the app, the code will stop at the marked line:

.. code:: bash

    MAV> api start small_demo.py
    AUTO> > c:\users\hamis_000\documents\vagranttesting\tmpdeleteme\small_demo.py(20)<module>()
    -> print "Location: %s" % v.location
	
Press **Enter** to bring up the **(Pdb)** prompt. This is where you can enter the commands to step through the code, show stack traces,
etc. For example the console output below shows the **w** command being used to output the current stack trace.

.. code:: bash

    AUTO>
   (Pdb) w
    c:\users\hamis_000\downloads\winpython-64bit-2.7.6.4\python-2.7.6.amd64\lib\threading.py(783)__bootstrap()
    cAUTO> :\users\hamis_000\downloads\winpython-64bit-2.7.6.4\python-2.7.6.amd64\lib\site-packages\droneapi\module\api.py(321)run()
    -> self.fn()amis_000\downloads\winpython-64bit-2.7.6.4\python-2.7.6.amd64\lib\threading.py(810)__bootstrap_inner()
    c:\users\hamis_000\downloads\winpython-64bit-2.7.6.4\python-2.7.6.amd64\lib\site-packages\droneapi\module\api.py(592)<lambda>()
    -> APIThread(self, lambda: execfile(args[1], g), args[1])
	
The available `debugger commands are listed here <https://docs.python.org/2/library/pdb.html#debugger-commands>`_. For more information 
about *pdb* see the `Python Debugger site <https://docs.python.org/2/library/pdb.html>`_.
	
.. note::

    *Pdb* commands must be entered in the **(Pdb)** prompt. If you press "Enter" in an empty prompt the previous command will be called
    again.  This is helpful if you want to **s** (step) through every line of code.


Other debuggers
===============

At time of writing we don't have information about how to debug DroneKit apps with other debuggers (although anecdotally *gdb* has 
successfully been used).

If you have information about how to set up and use other debuggers with DroneKit, please :ref:`contribute them <contributing>`.