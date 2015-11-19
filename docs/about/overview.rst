==============
About DroneKit
==============

DroneKit-Python allows developers to create apps that run on an onboard :ref:`companion computer <supported-companion-computers>` and communicate with the `ArduPilot <http://ardupilot.com>`_ flight controller using a low-latency link. Onboard apps can significantly enhance the autopilot, adding greater intelligence to vehicle behaviour, and performing tasks that are computationally intensive or time-sensitive (for example, computer vision, path planning, or 3D modelling). DroneKit-Python can also be used for ground station apps, communicating with vehicles over a higher latency RF-link. 

The API communicates with vehicles over MAVLink. It provides programmatic access to a connected vehicle's telemetry, state and parameter information, and enables both mission management and direct control over vehicle movement and operations.



Open source community
=====================

DroneKit-Python is an open source and community-driven project. 

You can find all the source code on `Github here <https://github.com/dronekit/dronekit-python>`_ and check out our permissive :doc:`Apache v2 Licence <license>`. 
If you want to join the community, then see our :doc:`contributing section <../contributing/index>` for lots of ideas on how you can help.


Compatibility
=============
DroneKit-Python is compatible with vehicles that communicate using the `MAVLink protocol <http://qgroundcontrol.org/mavlink/start>`_ (including most vehicles made by `3DR <https://3drobotics.com/>`_ and other members of the `DroneCode foundation <https://www.dronecode.org/about/project-members>`_). It runs on Linux, Mac OS X, or Windows.

.. note::

    DroneKit-Python is validated against, and hence *most compatible* with, the `ArduPilot UAV Platform <http://ardupilot.com/>`_. 
    Vehicles running other autopilots may be be less compatible due to differences in adhererence/interpretation of the MAVLink specification. 
    Please report any autopilot-specific issues `on Github here <https://github.com/dronekit/dronekit-python/issues>`_.



API features
============


The API provides classes and methods to:

- Connect to a vehicle (or multiple vehicles) from a script
- Get and set vehicle state/telemetry and parameter information.
- Receive asynchronous notification of state changes.
- Guide a UAV to specified position (GUIDED mode).
- Send arbitrary custom messages to control UAV movement and other hardware (GUIDED mode).
- Create and manage waypoint missions (AUTO mode).
- Override RC channel settings.

A complete API reference is available :ref:`here <api_reference>`.


Technical support
=================

This documentation is a great place to get started with developing DroneKit Python APIs. 

If you run into problems, the best place to ask questions is the `DroneKit-Python Forum <https://discuss.dronekit.io/c/python>`_. 
If your problem turns out to be a bug, then it should be `posted on Github <https://github.com/dronekit/dronekit-python/issues>`_.



