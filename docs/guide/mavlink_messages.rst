.. _mavlink_messages:

================
MAVLink Messages
================

Some useful MAVLink messages sent by the autopilot are not (yet) directly available to DroneKit-Python scripts
through the :ref:`observable attributes <vehicle_state_observe_attributes>` in :py:class:`Vehicle <dronekit.Vehicle>`.

This topic shows how you can intercept specific MAVLink messages by defining a listener callback function 
using the :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` decorator.

.. tip::

    :ref:`example_create_attribute` shows how you can extend this approach to create a new :py:class:`Vehicle <dronekit.Vehicle>`
    attribute in your client code.


.. _mavlink_messages_message_listener:
.. _mavlink_messages_set_mavlink_callback:

Creating a message listener
===========================

The :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` decorator can be used to 
set a particular function as the callback handler for a particular message type. You can create listeners 
for as many messages as you like, or even multiple listeners for the same message. 

For example, the code snippet below shows how to set a listener for the ``RANGEFINDER`` message:

.. code:: python

    #Create a message listener using the decorator.   
    @vehicle.on_message('RANGEFINDER')
    def listener(self, name, message):
        print message

.. tip::

    Every single listener can have the same name/prototpye as above ("``listener``") because
    Python does not notice the decorated functions are in the same scope.
    
    Unfortunately this also means that you can't unregister a callback created using this method.
    
The messages are `classes <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_ from the 
`pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_ library. 
The output of the code above looks something like:

.. code:: bash

    RANGEFINDER {distance : 0.0899999961257, voltage : 0.00900000054389}
    ...
    
You can access the message fields directly. For example, to access the ``RANGEFINDER`` message your listener
function might look like this:

.. code:: python

    #Create a message listener using the decorator.   
    @vehicle.on_message('RANGEFINDER')
    def listener(self, name, message):
        print 'distance: %s' % message.distance
        print 'voltage: %s' % message.voltage


Watching all messages
=====================

You can register a callback for *all messages* by setting the message name as the wildcard string ('``*``'):

.. code:: python

    #Create a message listener for all messages.   
    @vehicle.on_message('*')
    def listener(self, name, message):
        print 'message: %s' % message
        
        
Removing an observer
====================

Callbacks registered using the :py:func:`Vehicle.on_message() <dronekit.Vehicle.on_message>` decorator *cannot be removed*. 
This is generally not a problem, because in most cases you're interested in messages for the lifetime of a session.

If you do need to be able to remove messages you can instead add the callback using 
:py:func:`Vehicle.add_message_listener <dronekit.Vehicle.add_message_listener>`, and then remove it by calling 
:py:func:`Vehicle.remove_message_listener <dronekit.Vehicle.remove_message_listener>`.
