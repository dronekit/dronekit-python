===========================
Second Demo: Drone Delivery
===========================

This demonstration is a bit more extensive.  It is a `CherryPy <http://www.cherrypy.org>`_ based web application that displays a mapbox map to let you view the current vehicle position and send the vehicle commands to fly to a particular latitude and longitude.

New functionality demonstrated by this example includes:

* Using attribute observers to be notified of vehicle state changes.
* Starting *CherryPy* from a DroneKit application.


Starting the demo
=================

The demonstration is started similar to the previous tutorials.  You should see output that looks like the following:

::

	GUIDED> api start drone_delivery.py
	GUIDED> [DEBUG]: DroneDelivery Start
	[DEBUG]: Waiting for GPS Lock
	[DEBUG]: DroneDelivery Armed Callback
	[DEBUG]: GPS: GPSInfo:fix=3,num_sat=10
	[DEBUG]: Running initial boot sequence
	[DEBUG]: Arming
	[DEBUG]: Taking off
	[DEBUG]: Mode: GUIDED
	INFO:cherrypy.error:[03/Mar/2015:14:29:01] ENGINE Bus STARTING
	INFO:cherrypy.error:[03/Mar/2015:14:29:01] ENGINE Started monitor thread '_TimeoutMonitor'.
	INFO:cherrypy.error:[03/Mar/2015:14:29:01] ENGINE Started monitor thread 'Autoreloader'.
	INFO:cherrypy.error:[03/Mar/2015:14:29:01] ENGINE Serving on http://0.0.0.0:8080
	INFO:cherrypy.error:[03/Mar/2015:14:29:01] ENGINE Bus STARTED
	ARMED
	GPS lock at 0 meters

Screenshots
===========

You should be able to reach your new webserver at http://localhost:8080. It will look like the following:

.. image:: https://github.com/diydrones/droneapi-python/raw/master/example/documentation/drone-delivery-splash.png

.. image:: https://github.com/diydrones/droneapi-python/raw/master/example/documentation/drone-delivery-track.png

.. image:: https://github.com/diydrones/droneapi-python/raw/master/example/documentation/drone-delivery-command.png


Looking at the code
===================

Using attribute observers
-------------------------

All attributes in DroneKit can have observers - this is the primary mechanism you should use to be notified of changes in vehicle state.  For instance, `drone_delivery.py <https://github.com/diydrones/droneapi-python/blob/master/example/drone_delivery/drone_delivery.py>`_ calls:

:: 

	self.vehicle.add_attribute_observer('location', self.location_callback)

	...

    def location_callback(self, location):
        location = self.vehicle.location

        if location.alt is not None:
            self.altitude = location.alt

        self.current_location = location


This results in DroneKit calling our ``location_callback`` method any time the location attribute gets changed.

Starting CherryPy from a DroneKit application
---------------------------------------------

We start running a web server by calling ``cherrypy.engine.start()``.

*CherryPy* is a very small and simple webserver.  It is probably best to refer to their eight line `tutorial <http://www.cherrypy.org/>`_ for more information.

Next we'll look at the basics of using the webservice and the local vehicle API to 'replay' a flight which has been uploaded to `Droneshare <http://droneshare.com>`_.
