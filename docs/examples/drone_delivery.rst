===========================
Example: Drone Delivery
===========================

This example shows how to create a `CherryPy <http://www.cherrypy.org>`_ based web application that 
displays a mapbox map to let you view the current vehicle position and send the vehicle commands 
to fly to a particular latitude and longitude.

.. warning::

    At time of writing, this example does not work properly (the vehicle does not take off).
    For more information see `#357 Mode not changed when message sent inside drone delivery example <https://github.com/dronekit/dronekit-python/issues/357>`_

New functionality demonstrated by this example includes:

* Using attribute observers to be notified of vehicle state changes.
* Starting *CherryPy* from a DroneKit application.


Running the example
===================

The example can be run much as described in :doc:`running_examples` (which in turn assumes that the vehicle
and DroneKit have been set up as described in :ref:`get-started`). The main exception is that you need to 
install the CherryPy dependencies and view the behaviour in a web browser.
    
If you're using a simulated vehicle remember to :ref:`disable arming checks <disable-arming-checks>` so 
that the example can run. You can also `add a virtual rangefinder <http://dev.ardupilot.com/wiki/simulation-2/sitl-simulator-software-in-the-loop/using-sitl-for-ardupilot-testing/#adding_a_virtual_rangefinder>`_
(otherwise the :py:attr:`Vehicle.rangefinder <dronekit.lib.Vehicle.rangefinder>` attribute may return values of ``None`` for the distance
and voltage). 

In summary, after cloning the repository:

#. Navigate to the example folder as shown:

   .. code-block:: bash

       cd dronekit-python\examples\drone_delivery\


#. Install *CherryPy* and any other dependencies from **requirements.pip** in that directory:

   .. code-block:: bash

       pip install -r requirements.pip
       
       
#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python drone_delivery.py --connect 127.0.0.1:14550

   .. note::
   
       The command parameter above is the default, and may be omitted. This
       connects to SITL on udp port 127.0.0.1:14550.

#. After a short while you should be able to reach your new webserver at http://localhost:8080. 


On the command prompt you should see (something like):

.. code-block:: bash

    \dronekit-python\examples\drone_delivery>drone_delivery.py
    local path: E:\deleteme\dronekit-python\examples\drone_delivery
    Connecting to vehicle on: 127.0.0.1:14550
    >>> ☺APM:Copter V3.4-dev (e0810c2e)
    >>> ☺Frame: QUAD
    connected ...
    [DEBUG]: DroneDelivery Start
    [DEBUG]: Waiting for GPS Lock
    [DEBUG]: DroneDelivery Armed Callback
    [DEBUG]: GPS: GPSInfo:fix=3,num_sat=10
    [DEBUG]: Running initial boot sequence
    [DEBUG]: Arming
    [DEBUG]: Taking off
    [DEBUG]: Mode: GUIDED
    INFO:cherrypy.error:[21/Oct/2015:16:33:15] ENGINE Bus STARTING
    INFO:cherrypy.error:[21/Oct/2015:16:33:15] ENGINE Started monitor thread 'Autoreloader'.
    INFO:cherrypy.error:[21/Oct/2015:16:33:15] ENGINE Started monitor thread '_TimeoutMonitor'.
    INFO:cherrypy.error:[21/Oct/2015:16:33:15] ENGINE Serving on http://0.0.0.0:8080
    INFO:cherrypy.error:[21/Oct/2015:16:33:15] ENGINE Bus STARTED
    >>> ☺ARMING MOTORS
    >>> ☺Initialising APM...
    ...
    

Screenshots
===========

The webserver (http://localhost:8080) will look like the following:

.. image:: drone-delivery-splash.png

.. image:: drone-delivery-track.png

.. image:: drone-delivery-command.png


How it works
============

Using attribute observers
-------------------------

All attributes in DroneKit can have observers - this is the primary mechanism you should use to be notified of changes in vehicle state.  For instance, `drone_delivery.py <https://github.com/dronekit/dronekit-python/blob/master/examples/drone_delivery/drone_delivery.py>`_ calls:

.. code-block:: python

    self.vehicle.add_attribute_observer('location', self.location_callback)

    ...

    def location_callback(self, location):
        location = self.vehicle.location.global_frame

        if location.alt is not None:
            self.altitude = location.alt

        self.current_location = location


This results in DroneKit calling our ``location_callback`` method any time the location attribute gets changed.



Starting CherryPy from a DroneKit application
---------------------------------------------

We start running a web server by calling ``cherrypy.engine.start()``.

*CherryPy* is a very small and simple webserver.  It is probably best to refer to their eight line `tutorial <http://www.cherrypy.org/>`_ for more information.



Source code
===========

The full source code at documentation build-time is listed below (`current version on github <https://github.com/dronekit/dronekit-python/blob/master/examples/drone_delivery/drone_delivery.py>`_):

.. include:: ../../examples/drone_delivery/drone_delivery.py
    :literal:
