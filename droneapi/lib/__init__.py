# DroneAPI module

"""
This is the API Reference for the DroneKit-Python API.

The main API is the :py:class:`Vehicle <droneapi.lib.Vehicle>` class. 
The code snippet below shows how to obtain an instance of the (first) connected vehicle:

.. code:: python

    # Get a local APIConnection to the autopilot (from companion computer or GCS).
    api_connection = local_connect()
    # Get the first connected vehicle from the APIConnection
    vehicle = api.get_vehicles()[0]

:py:class:`Vehicle <droneapi.lib.Vehicle>` provides access to vehicle *state* through python attributes (e.g. :py:attr:`Vehicle.location <droneapi.lib.Vehicle.location>`) 
and to settings/parameters though the :py:attr:`Vehicle.parameters <droneapi.lib.Vehicle.parameters>` attribute. 
Asynchronous notification on vehicle state-change is available by registering observers (callbacks) for attribute or parameter changes.

:py:class:`Vehicle <droneapi.lib.Vehicle>` provides two main ways to control vehicle movement and other operations:
    
* Missions are downloaded and uploaded through the :py:attr:`Vehicle.commands <droneapi.lib.Vehicle.commands>` attribute 
  (see :py:class:`CommandSequence <droneapi.lib.CommandSequence>` for more information).
* Direct control of movement outside of missions is also supported. To set a target position you can use :py:func:`CommandSequence.goto <droneapi.lib.CommandSequence.goto>`. 
  Control over speed, direction, altitude, camera trigger and any other aspect of the vehicle is supported using custom MAVLink messages 
  (:py:func:`Vehicle.send_mavlink <droneapi.lib.Vehicle.send_mavlink>`, :py:func:`Vehicle.message_factory <droneapi.lib.Vehicle.message_factory>`).

A number of other useful classes and methods are listed below.

----

.. todo:: Update this when have confirmed how to register for parameter notifications.
"""

import threading
from pymavlink import mavutil

local_path = ''



def web_connect(authinfo):
    """
    .. warning:: This API is not fully implemented and should not be used.

    Connect to the central dronehub server.
    
    :param AuthInfo authinfo: A container for authentication information (username, password, challenge info, etc.)
    """
    return APIConnection()

def local_connect():
    """
    Connect to the API provider for the local vehicle or ground control station.

    :return: The API provider.
    :rtype: APIConnection
    """
    return APIConnection()

class APIException(Exception):
    """
    Base class for DroneKit related exceptions.
    
    :param String msg: Message string describing the exception
    """

    def __init__(self, msg):
        self.msg = msg

class AuthInfo(object):
    """
    Not implemented. This is part of a (currently) internal API.
	
    .. INTERNAL NOTE: Base class for various authentication flavors.

        Currently only simple username & password authentication are supported

        :param object: username/password values.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

class ConnectionInfo(object):
    """
    Internal API. Do not use.

    Connection information object used by MAVProxy.
    """

    def __init__(self, mavproxy_options):
        self.maxproxy_options = mavproxy_options

class Attitude(object):
    """
    Attitude information.

    .. figure:: http://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Yaw_Axis_Corrected.svg/500px-Yaw_Axis_Corrected.svg.png
        :width: 400px
        :alt: Diagram showing Pitch, Roll, Yaw
        :target: http://commons.wikimedia.org/wiki/File:Yaw_Axis_Corrected.svg
        
        Diagram showing Pitch, Roll, Yaw (`Creative Commons <http://commons.wikimedia.org/wiki/File:Yaw_Axis_Corrected.svg>`_)

    :param pitch: Pitch in radians
    :param yaw: Yaw in radians
    :param roll: Roll in radians
    """
    def __init__(self, pitch, yaw, roll):
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll

    def __str__(self):
        return "Attitude:pitch=%s,yaw=%s,roll=%s" % (self.pitch, self.yaw, self.roll)

class Location(object):
    """
    A location object.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_. The altitude is relative to either the *home position* or "mean sea-level", depending on the value of the ``is_relative``.

    For example, a location object might be defined as:

    .. code:: python

       Location(-34.364114, 149.166022, 30, is_relative=True)

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    :param lat: Latitude.
    :param lon: Longitude.
    :param alt: Altitude in meters (either relative or absolute).
    :param is_relative: ``True`` if the specified altitude is relative to a 'home' location (this is usually desirable). ``False`` to set altitude relative to "mean sea-level".
    """
    def __init__(self, lat, lon, alt=None, is_relative=True):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.is_relative = is_relative

    def __str__(self):
        return "Location:lat=%s,lon=%s,alt=%s,is_relative=%s" % (self.lat, self.lon, self.alt, self.is_relative)

class GPSInfo(object):
    """
    Standard information available about GPS.
	
    If there is no GPS lock the parameters are set to ``None``.

    :param IntType eph: GPS horizontal dilution of position (HDOP) in cm (m*100).
    :param IntType epv: GPS horizontal dilution of position (VDOP) in cm (m*100). 
    :param IntType fix_type: 0-1: no fix, 2: 2D fix, 3: 3D fix
    :param IntType satellites_visible: Number of satellites visible.

    .. todo:: FIXME: GPSInfo class - possibly normalize eph/epv?  report fix type as string?

    .. todo:: Confirm the values returned if value unknown by GPS. Confirm descriptions. Confirm  units. For eph "If unknown, set to: TBD ?Max value of type" , "If unknown, set to: TBD  ?Max value of IntType?". fpr satellites visible:  If unknown, set to 255
        
    """
    def __init__(self, eph, epv, fix_type, satellites_visible):
        self.eph = eph
        self.epv = epv
        self.fix_type = fix_type
        self.satellites_visible = satellites_visible

    def __str__(self):
        return "GPSInfo:fix=%s,num_sat=%s" % (self.fix_type, self.satellites_visible)


class VehicleMode(object):
    """
    This object is used to get and set the current "flight mode". 
	
    The flight mode determines the behaviour of the vehicle, and what commands it can obey. For example, 
    the AUTO mode is used (on all vehicle platforms) when executing stored waypoint missions.

    The set of supported flight modes is vehicle-specific. For information about what modes are supported on each platform see: `Copter <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/>`_, `Plane <http://plane.ardupilot.com/wiki/flying/flight-modes/>`_, `Rover <http://rover.ardupilot.com/wiki/configuration-2/#mode_meanings>`_.

    The :py:attr:`Vehicle.mode <droneapi.lib.Vehicle.mode>` can be queried for the current mode. The code snippet below shows how to observe changes to the mode:
	
    .. code:: python

        def mode_callback(self, mode):
            print "Vehicle Mode", vehicle.mode

        vehicle.add_attribute_observer('mode', mode_callback)

	
    The code snippet below shows how to change the vehicle mode to AUTO:

    .. code:: python

        # Get an instance of the API endpoint and a vehicle
        api = local_connect()
        vehicle = api.get_vehicles()[0]
		
        # Set the vehicle into auto mode
        vehicle.mode = VehicleMode("AUTO")

    .. py:attribute:: name 

        The mode name, as a ``string``.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "VehicleMode:%s" % self.name

class APIConnection(object):
    """
    An API provider.

    This is the top level API connection returned from :py:func:`local_connect()`.  You should not manually create instances of
    this class.

    .. INTERNAL_COMMENT: This is also returned by :py:func:`web_connect()` (not supported/fully implemented).
    """

    def get_vehicles(self, query=None):
        """
        Get the set of vehicles that are controllable from this connection.

        For example, to get the first vehicle in the set with ``get_vehicles()``:

        .. code:: python

            api = local_connect()     # Get an APIConnection
            first_vehicle = api.get_vehicles()[0]

        .. note::   

            The set of vehicles connected by the API is configured through MAVProxy. When running on a companion computer there will only ever
            be one ``Vehicle`` in the returned set. A ground control station might potentially control (and hence return) more than one vehicle. 


        :param query: This parameter is ignored. Use the default.
        :returns: Set of :py:class:`Vehicle` objects controllable from this connection.      
        """
        # return [ Vehicle(), Vehicle() ]
        raise Exception("Subclasses must override")

    @property
    def exit(self):
        """
        True if the current thread has been asked to exit.

        The connection to the UAV is owned by MAVProxy, which uses this property to signal that the thread should be closed (for whatever reason).
        Scripts are expected to check the property and close the thread if this if ``True``. For example:

        .. code:: python

            while not api.exit:
                # send commands to vehicle etc.

        .. todo:: FIXME: APIConnection.exit - should this be private, or even part of the drone api at all?
        """
        return threading.current_thread().exit

class HasObservers(object):
    def __init__(self):
        # A mapping from attr_name to a list of observers
        self.__observers = {}

    """
    Provides callback based notification on attribute changes.

    The argument list for observer is ``observer(attr_name)``.
    """
    def add_attribute_observer(self, attr_name, observer):
        """
        Add an attribute observer.
		
        The observer is called with the ``attr_name`` argument. This can be used to access
        the vehicle parameter, as shown below:
		
        .. code:: python

            #Add observer for the vehicle's current location
            vehicle.add_attribute_observer('location', location_callback)
            
            #Callback to print the location 
            def location_callback(location):
                print "Location: ", vehicle.location
          


        .. note:: 
            Attribute changes will only be published for changes due to some other entity.  
            They will not be published for changes made by the local API client 
            (in order to prevent redundant notification for local changes).

        :param attr_name: The attribute to watch.
        :param observer: The callback to invoke when a change in the attribute is detected.
		
        .. todo:: Check that the defect for endless repetition after thread closes is fixed: https://github.com/diydrones/dronekit-python/issues/74		
        """
        l = self.__observers.get(attr_name)
        if l is None:
            l = []
            self.__observers[attr_name] = l
        l.append(observer)

    def remove_attribute_observer(self, attr_name, observer):
        """
        Remove an observer.

        For example, the following line would remove a previously added vehicle 'location' observer called location_callback:

        .. code:: python

            vehicle.remove_attribute_observer('location', location_callback)
            

        :param attr_name: The attribute name that is to have an observer removed.
        :param observer: The callback function to remove.
        

        """
        l = self.__observers.get(attr_name)
        if l is not None:
            l.remove(observer)
            if len(l) == 0:
                del self.__observers[attr_name]

    def notify_observers(self, attr_name):
        """
        Internal function. Do not use.

        This method calls observers when the named attribute has changed.

        .. INTERNAL NOTE: (For subclass use only) 
        """
        # print "Notify: " + attr_name
        l = self.__observers.get(attr_name)
        if l is not None:
            for o in l:
                try:
                    o(attr_name)
                except TypeError as e:
                    # This is commonly called by a bad argument list
                    print("TypeError calling observer: ", e)
                except Exception as e:
                    print("Error calling observer: ", e)

class Vehicle(HasObservers):
    """
    The main vehicle API

    Asynchronous notification on change of vehicle state is available by registering observers (callbacks) for attribute or
    parameter changes.

    Most vehicle state is exposed through python attributes (e.g. ``vehicle.location``). Most of these attributes are
    auto-populated based on the capabilities of the connected autopilot/vehicle.

    Particular autopilots/vehicles may define different attributes from this standard list (extra batteries, GPIOs, etc.)
    However if a standard attribute is defined it must follow the rules specified below.
	
    **Autopilot specific attributes & types:**

    To prevent name clashes the following naming convention should be used:
    
    * ``ap_<name>`` - For autopilot specific parameters (apm 2.5, pixhawk etc.). For example "ap_pin5_mode" and "ap_pin5_value".
    * ``user_<name>`` - For user specific parameters

    **Standard attributes & types:**
    
    .. py:attribute:: location

        Current :py:class:`Location`.

    .. py:attribute:: waypoint_home

        Home waypoint/position (:py:class:`Command`).

        .. todo:: Confirm the type - I think it is a command, not waypoint as originally listed in table. 


    .. py:attribute:: attitude

        Current vehicle :py:class:`Attitude` (pitch, yaw, roll).


    .. py:attribute:: velocity

        Current velocity as a three element list [ vx, vy, vz ] (in meter/sec).


    .. py:attribute:: mode

        This attribute is used to get and set the current flight mode (:py:class:`VehicleMode`).


    .. py:attribute:: airspeed

        Current airspeed in metres/second (``double``).

        .. todo:: FIXME: Should airspeed value move somewhere else from "Standard attributes & types" table?

    .. py:attribute:: groundspeed

        Groundspeed in metres/second (``double``).

    .. py:attribute:: gps_0

        GPS position information (:py:class:`GPSInfo`).


    .. py:attribute:: battery_0_soc

        Not implemented (``double``).
		
        .. todo:: Not implemented - update when this closed: https://github.com/diydrones/dronekit-python/issues/71

    .. py:attribute:: battery_0_volt

        Not implemented (``double``).
		
        .. todo:: Not implemented - update when this closed: https://github.com/diydrones/dronekit-python/issues/71

    .. py:attribute:: armed

        This attribute can be used to get and set the ``armed` state of the vehicle (``boolean``).
		
        The code below shows how to read the state, and to arm/disam the vehicle:
		
        .. code:: python

            # Print the armed state for the vehicle
            print "Armed: %s" % vehicle.armed

            # Disarm the vehicle
            vehicle.armed = False
			
            # Arm the vehicle
            vehicle.armed = True


        
    .. py:attribute:: channel_override
	
        .. warning::
		
            RC override may be useful for simulating user input and when implementing certain types of joystick control. It should not be used 
            for direct control of vehicle channels unless there is no other choice! 

            Instead use the appropriate MAVLink commands like DO_SET_SERVO/DO_SET_RELAY, or more generally
            set the desired position or direction/speed.

        This attribute takes a dictionary argument defining the RC *output* channels to be overridden (specified by channel number), and their new values.  
        Channels that are not specified in the dictionary are not overridden. All multi-channel updates are atomic.
		
        To cancel an override call ``channel_override`` again, setting zero for the overridden channels.
		
        The values of the first four channels map to the main flight controls: 1=Roll, 2=Pitch, 3=Throttle, 4=Yaw (the mapping is defined in ``RCMAP_`` parameters: 
        `Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/#rcmap__parameters>`_, 
        `Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/#rcmap__parameters>`_ , 
        `Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/#rcmap__parameters>`_).
	
        The remaining channel values are configurable, and their purpose can be determined using the 
        `RCn_FUNCTION parameters <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/>`_. 
        In general a value of 0 set for a specific ``RCn_FUNCTION`` indicates that the channel can be 
        `mission controlled <http://plane.ardupilot.com/wiki/flight-features/channel-output-functions/#disabled>`_ (i.e. it will not directly be 
        controlled by normal autopilot code).

        An example of setting and clearing the override is given below: 

        .. code:: python

            # Override channels 1 and 4 (only).
            vehicle.channel_override = { "1" : 900, "4" : 1000 }  
            vehicle.flush()
			
            # Cancel override on channel 1 and 4 by sending 0
            vehicle.channel_override = { "1" : 0, "4" : 0 }
            vehicle.flush()


        .. versionchanged:: 1.0
    
            This update replaces ``rc_override`` with ``channel_override``/``channel_readback`` documentation.


        .. todo:: Add note to the examples/guide like warning above not to use this mechanism except as intended:
		
            https://github.com/diydrones/dronekit-python/issues/72
			
        .. todo:: 
    
            channel_override/channel_readback documentation

            In a future update strings will be defined per vehicle type ('pitch', 'yaw', 'roll' etc...)
            and rather than setting channel 3 to 1400 (for instance), you will pass in a dict with
            'throttle':1200.  
      
            This change will be useful in two ways:
        
            * we can hide (eventually we can deprecate) any notion of rc channel numbers at all.
            * vehicles can eventually define new 'channels' for overridden values.
        
            FIXME: Remaining channel_override/channel_readback FIXMEs:
        
            * how to address the units issue?  Merely with documentation or some other way?
            * is there any benefit of using lists rather than tuples for these attributes


    .. py:attribute:: channel_readback

        This read-only attribute returns a dictionary containing the *original* vehicle RC channel values (ignoring any overrides set using 
        :py:attr:`channel_override <droneapi.lib.Vehicle.channel_override>`). Dictionary entries have the format ``channelName -> value``.

        For example, the returned dictionary might look like this: 

        .. code:: python
		
            RC readback: {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800} ? Dictionary () (read only)
			

			
    .. todo:: In V2, there may be ardupilot specific attributes & types (as in the introduction). If so, text below might be useful.
	
        (see `client_sketch.py#L76 <https://github.com/diydrones/dronekit-python/blob/master/example/sketch/client_sketch.py#L76>`_) 
	
        **Autopilot specific attributes & types:**

        .. py:attribute:: ap_pin5_mode

            string (adc, dout, din)

        .. py:attribute:: ap_pin5_value

            ? double (0, 1, 2.3 etc...)

    """

    def __init__(self):
        super(HasObservers,self).__init__()
        self.mavrx_callback = None

    @property
    def commands(self):
        """
        Gets the editable waypoints for this vehicle (the current "mission").
		
        This can be used to get, create, and modify a mission. It can also be used for direct control of vehicle position 
        (outside missions) using the :py:func:`goto <droneapi.lib.CommandSequence.goto>` method. 
        
        :returns: A :py:class:`CommandSequence` containing the waypoints for this vehicle.
        """
        None

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle (:py:class:`Parameters <droneapi.lib.Parameters>`).
        """
        return self._parameters

    def delete(self):
        """
        Delete this vehicle object.

        This requests deletion of the Vehicle object on the server. This operation may throw an exception on failure (i.e. for
        local connections or insufficient user permissions).
		
        It is not supported for local connections.
        """
        pass

    def get_mission(self, query_params):
        """
        Not implemented.

        Returns an object providing access to historical missions.

        .. warning:: Mission objects are only accessible from the REST API in release 1 (most use-cases requiring missions prefer a REST interface). The :class:`Mission` class has an empty implementation in DroneKit-Python release 1. 

        :param query_params: Some set of arguments that can be used to find a past mission
        :return: Mission - the mission object.

        .. todo:: FIXME: get_mission needs to be updated when class Mission is implemented. The warning needs to be removed and the values of the query_params specified.
        """
        
        return Mission()

    @property
    def message_factory(self):
        """
        Returns an object that can be used to create 'raw' MAVLink messages that are appropriate for this vehicle. 
        The message can then be sent using :py:func:`send_mavlink(message) <droneapi.lib.Vehicle.send_mavlink>`.
		
        These message types are defined in the central MAVLink github repository.  For example, a Pixhawk understands
        the following messages (from `pixhawk.xml <https://github.com/mavlink/mavlink/blob/master/message_definitions/v1.0/pixhawk.xml>`_): 

        .. code:: xml

          <message id="153" name="IMAGE_TRIGGER_CONTROL">
               <field type="uint8_t" name="enable">0 to disable, 1 to enable</field>
          </message>

        The name of the factory method will always be the lower case version of the message name with *_encode* appended.
        Each field in the XML message definition must be listed as arguments to this factory method.  So for this example
        message, the call would be:

        .. code:: python		

            msg = vehicle.message_factory.image_trigger_control_encode(True)
            vehicle.send_mavlink(msg)
	
        There is no need to specify the system id, component id or sequence number of messages (if defined in the message type) as the 
        API will set these appropriately when the message is sent.

        .. todo:: When I have a custom message guide topic. Link from here to it.

        .. todo:: Check if the standard MAV_CMD messages can be sent this way too, and if so add link.
        """
        None

    def send_mavlink(self, message):
        """
        This method is used to send raw MAVLink "custom messages" to the vehicle. 

        The function can send arbitrary messages/commands to a vehicle at any time and in any vehicle mode. It is particularly useful for
        controlling vehicles outside of missions (for example, in GUIDED mode).
		
        The :py:func:`message_factory <droneapi.lib.Vehicle.message_factory>` is used to create messages in the appropriate format. 
        Callers do not need to populate sysId/componentId/crc in the packet as the method will take care of that before sending.

        :param: message: A ``MAVLink_message`` instance, created using :py:func:`message_factory <droneapi.lib.Vehicle.message_factory>`.  
            There is need to specify the system id, component id or sequence number of messages as the API will set these appropriately.
        """
        pass


    def set_mavlink_callback(self, callback):
        """
        Provides asynchronous notification when any MAVLink packet is received from this vehicle.

        .. tip:: 

            This method is implemented - but we hope you don't need it.

            Because of the asynchronous attribute/waypoint/parameter notifications there should be no need for
            API clients to see raw MAVLink.  Please provide feedback if we missed a use-case.
			
        The code snippet below shows how to set a "demo" callback function as the callback handler:
		
        .. code:: python		

            # Demo callback handler for raw MAVLink messages
            def mavrx_debug_handler(message):
                print "Received", message

            # Set MAVLink callback handler (after getting Vehicle instance)			
            vehicle.set_mavlink_callback(mavrx_debug_handler)

        """
        self.mavrx_callback = callback

    def flush(self):
        """
        It is important to understand that setting attributes/changing vehicle state may occur over a slow link.

        It is **not** guaranteed that the effects of previous commands will be visible from reading vehicle attributes unless
        ``flush()`` is called first.  After the return from flush any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.
        """
        pass

#===============================================================================
#     def __getattr__(self, name):
#         """
#         Attributes are automatically populated based on vehicle type.
#
#         This override provides that behavior.
#         """
#
#         try:
#             return self.__dict[name]
#         except KeyError:
#             msg = "'{0}' object has no attribute '{1}'"
#             raise AttributeError(msg.format(type(self).__name__, name))
#
#     def __setattr__(self, name, value):
#         """
#         An override to support setting for vehicle attributes.
#
#         Note: Exceptions due to loss of communications, missing attributes or insufficient permissions are not guaranteed
#         to be thrown from inside this method.  Most failures will not be seen until flush() is called.  If you require immediate
#         notification of failure set autoflush.
#         """
#         pass
#===============================================================================

class Mission(object):
    """
    Access to historical missions.

    .. warning:: This function is a *placeholder*. It has no implementation in DroneKit-Python release 1. 

	    Mission objects are only accessible from the REST API in release 1 (most use-cases requiring missions prefer a REST interface).

    .. todo:: FIXME: Mission class needs to be updated when it is implemented (after DroneKit Python release 1).
    """
    pass

class Parameters(HasObservers):
    """
    This object is used to get and set the values of named parameters for a vehicle. See the following links for information on the supported parameters for each platform: `Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/>`_, `Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/>`_, `Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/>`_).
	
    Attribute names are generated automatically based on parameter names.  The example below shows how to get and set the value of a parameter.
    Note that 'set' operations are not guaranteed to be complete until :py:func:`flush() <Vehicle.flush>` is called on the parent :py:class:`Vehicle` object.
	
    .. code:: python

        # Print the value of the THR_MIN parameter.
        print "Param: %s" % vehicle.parameters['THR_MIN']

        # Change the parameter value to something different.
        vehicle.parameters['THR_MIN']=100
        vehicle.flush()

    .. todo:: Check above is correct. It isn't really attribute names, but the index key for parameters that are based on parameters names. Also, why does this HasObservers.
    .. todo:: Why does this implement HasObservers? How would you observe them?
    """

class Command(mavutil.mavlink.MAVLink_mission_item_message):
    """
    A waypoint object.
    
    This object encodes a single mission item command. The set of commands that are supported by ArduPilot in Copter, Plane and Rover (along with their parameters) 
    are listed in the wiki article `MAVLink Mission Command Messages (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.

    For example, to create a `NAV_WAYPOINT <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_nav_waypoint>`_ command:

    .. code:: python

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,-34.364114, 149.166022, 30)

	
    :param target_system: The id number of the message's target system (drone, GSC) within the MAVLink network. Set this to zero (broadcast) when communicating with a companion computer. 
    :param target_component: The id of a component the message should be routed to within the target system (for example, the camera). Set to zero (broadcast) in most cases.
    :param seq: The sequence number within the mission (the autopilot will reject messages sent out of sequence). This should be set to zero as the API will automatically set the correct value when uploading a mission.
    :param frame: The frame of reference used for the location parameters (x, y, z). In most cases this will be ``mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT``, which uses the WGS84 global coordinate system for latitude and longitude, but sets altitude as relative to the home position in metres (home altitude = 0). For more information `see the wiki here <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#frames_of_reference>`_.
    :param command: The specific mission command (e.g. ``mavutil.mavlink.MAV_CMD_NAV_WAYPOINT``). The supported commands (and command parameters are listed `on the wiki <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.    
    :param current: Set to zero (not supported).
    :param autocontinue: Set to zero (not supported).
    :param param1: Command specific parameter (depends on specific `Mission Command (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_).
    :param param2: Command specific parameter.
    :param param3: Command specific parameter.
    :param param4: Command specific parameter.
    :param x: (param5) Command specific parameter used for latitude (if relevant to command).
    :param y: (param6) Command specific parameter used for longitude (if relevant to command).
    :param z: (param7) Command specific parameter used for altitude (if relevant). The reference frame for altitude depends on the ``frame``.

    .. todo:: Confirm if target_sytem, target_component, seq, frame are all handled for you or not. If not, check that these are correct.
    .. todo:: FIXME: Command class - for now we just inherit the standard MAVLink mission item contents.
    """
    pass

class CommandSequence(object):
    """
    A sequence of vehicle waypoints (a "mission").

    Operations include 'array style' indexed access to the various contained waypoints.

    The current commands/mission for a vehicle are accessed using the :py:attr:`Vehicle.commands <droneapi.lib.Vehicle.commands>` attribute. Waypoints are not downloaded from vehicle until :py:func:`download()` is called.  The download is asynchronous; use :py:func:`wait_valid()` to block your thread until the download is complete.
	
    The code to download the commands from a vehicle is shown below:
	
    .. code-block:: python
        :emphasize-lines: 5-10

        # Connect to API provider and get vehicle	
        api = local_connect()
        vehicle = api.get_vehicles()[0]

        # Download the vehicle waypoints (commands). Wait until download is complete.
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_valid()

    The set of commands can be changed and uploaded to the client. The changes are not guaranteed to be complete until :py:func:`flush() <Vehicle.flush>` is called on the parent :py:class:`Vehicle` object.

    .. code:: python

        cmds = vehicle.commands
        cmds.clear()
        lat = -34.364114, 
        lon = 149.166022
        altitude = 30.0
        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 0, 0, 0, 0, 0,
            lat, lon, altitude)
        cmds.add(cmd)
        vehicle.flush()	



    .. todo:: HW Add CommandSequence.takeoff - should be in public API: https://github.com/diydrones/dronekit-python/issues/64
    """

    def download(self):
        '''
		Download all waypoints from the vehicle.
		
		The download is asynchronous. Use :py:func:`wait_valid()` to block your thread until the download is complete.
		'''
        pass

    def wait_valid(self):
        '''
		Block the calling thread until waypoints have been downloaded.
		
		This can be called after :py:func:`download()` to block the thread until the asynchronous download is complete.
		'''
        pass

    def goto(self, location):
        '''
        Go to a specified location (changing :py:class:`VehicleMode` to ``GUIDED`` if necessary).

        .. code:: python

            # Set mode to guided - this is optional as the goto method will change the mode if needed.	
            vehicle.mode = VehicleMode("GUIDED")
            
            # Set the location to goto() and flush()
            a_location = Location(-34.364114, 149.166022, 30, is_relative=True)
            vehicle.commands.goto(a_location)
            vehicle.flush()

        :param Location location: The target location.
        '''
        pass

    def clear(self):
        '''
        Clear the command list.
        '''
        pass

    def add(self, cmd):
        '''
        Add a new command (waypoint) at the end of the command list.

        :param Command cmd: The command to be added.
        '''
        pass

    @property
    def count(self):
        '''
		Return number of waypoints.
		
		:return: The number of waypoints in the sequence.
		'''
        return 0

    @property
    def next(self):
        """
        Get the currently active waypoint number.

        .. INTERNAL NOTE: (implementation provided by subclass)
        """
        return None

    @next.setter
    def next(self, value):
        """
        Set a new ``next`` waypoint for the vehicle.

        .. INTERNAL NOTE: (implementation provided by subclass)
        """
        pass


