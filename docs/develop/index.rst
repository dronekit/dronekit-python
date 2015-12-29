========================
Developing with DroneKit 
========================

DroneKit-Python is primarily intended for use on Linux-based :doc:`companion-computers` that travel 
on a vehicle and communicate with the autopilot via a serial port. It can also be used 
on ground-based computers running Linux, Windows or Mac OSX (communicating using WiFi or a telemetry radio). 

During development you'll generally run it on a development computer, communicating with a 
:doc:`simulated vehicle<sitl_setup>` running on the same machine (via a UDP connection).

This section contains topics explaining how to develop with DroneKit-Python, 
covering subjects like installation, setting up the target vehicle or simulator, best practices 
and coding standards.


.. toctree::
    :maxdepth: 1

    installation
    companion-computers
    Simulated Vehicle <sitl_setup>
    best_practice
    coding_standards