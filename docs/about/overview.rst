==============
About DroneKit
==============

DroneKit-Python is DroneKit's main API for *Air Computing* — allowing developers to create apps that run on an onboard :ref:`companion computer <supported-companion-computers>` and communicate with the `ArduPilot <http://ardupilot.com>`_ flight controller using a low-latency link. *Air apps* can significantly enhance the autopilot, adding greater intelligence to vehicle behaviour, and performing tasks that are computationally intensive or time-sensitive (for example, computer vision, path planning, or 3D modelling). 

The API communicates with "locally connected" vehicles over MAVLink. It provides programmatic access to a connected vehicle's telemetry, state and parameter information, and enables both mission management and direct control over vehicle movement and operations.


Open source community
=====================

DroneKit-Python is an open source and community-driven project. 

You can find all the source code on `Github here <https://github.com/diydrones/dronekit-python>`_ and check out our permissive :doc:`Apache v2 Licence <license>`. 
If you want to join the community, then see our :doc:`contributing page <contributing>` for lots of ideas on how you can help.


Compatibility
=============
DroneKit-Python is compatible with all vehicles using the `MAVLink protocol <http://qgroundcontrol.org/mavlink/start>`_ (including most vehicles made by 3DR and other members of the `DroneCode foundation <https://www.dronecode.org/about/project-members>`_). It runs on Linux, Mac OS X, or Windows. 

In addition to "Air apps", it can be used to create apps that run on a desktop ground station and communicate with ArduPilot over a higher latency RF-link. 


API features
============


The API provides classes and methods to:

- Get a list of connected vehicles.
- Get and set vehicle state/telemetry and parameter information.
- Receive asynchronous notification of state changes.
- Create and manage waypoint missions (AUTO mode).
- Guide a UAV to specified position (GUIDED mode).
- Send arbitrary custom messages to control UAV movement and other hardware (GUIDED mode).
- Override RC channel settings.

A complete API reference is available :ref:`here <api_reference>`.


Technical support
=================

This documentation is a great place to get started with developing DroneKit Python APIs. 

If you run into problems, the `best place to ask questions is Stack Overflow <http://stackoverflow.com/questions/tagged/dronekit-python>`_. 
If your problem turns out to be a bug, then it should be `posted on Github <https://github.com/diydrones/dronekit-python/issues>`_.



