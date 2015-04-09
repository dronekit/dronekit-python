# DroneAPI module
import threading
from pymavlink import mavutil

local_path = ''

def web_connect(authinfo):
    """
    Connect to the central dronehub server

    :param AuthInfo authinfo: A container for authentication information (username, password, challenge info, etc.)
    """
    return APIConnection()

def local_connect():
    """
    Connect to the API provider for the local GCS (or vehicle if running on vehicle)
    """
    return APIConnection()

class APIException(Exception):
    """Base class for DroneAPI related exceptions."""

    def __init__(self, msg):
        self.msg = msg

class AuthInfo(object):
    """
    Base class for various authentication flavors.
	
    Currently only simple username & password authentication are supported
	
    :param object: username/password values.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

class ConnectionInfo(object):
    """
    Connection information for contacting the local vehicle.
	
	.. todo:: ConnectionInfo - what is the format of the options?
    """
    def __init__(self, mavproxy_options):
        self.maxproxy_options = mavproxy_options

class Attitude(object):
    """
    Attitude information.

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

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    :param lat: Latitude
    :param lon: Longitude
    :param alt: Altitude in meters (either relative or absolute)
    :param is_relative: True if the specified altitude is relative to a 'home' location
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
    Standard information available about GPS

    .. todo:: FIXME: GPSInfo class - possibly normalize eph/epv?  report fix type as string?
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
    Vehicle mode information

    Supported properties:

    ============= ======================================
    Name          Description
    ============= ======================================
    name          string - the mode name (AUTO etc...)
    ============= ======================================

    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "VehicleMode:%s" % self.name

class APIConnection(object):
    """
    An API provider.

    This is the top level API connection returned from :py:func:`local_connect()` or :py:func:`web_connect()`.  You should not manually create instances of
    this class.
    """

    def get_vehicles(self, query=None):
        """
        Get the set of vehicles that are controllable from this connection.

        :param query: This parameter will be documented with the web API, for now just use the default.
        """
        # return [ Vehicle(), Vehicle() ]
        raise Exception("Subclasses must override")

    @property
    def exit(self):
        """
        Has our thread been asked to exit?

        Unfortunately python has no standard convention for requesting thread exit, since API scripts might be invoked from inside
        of GCS applications where the user wants control of what scripts are running, this property provides a standard way of
        checking for exit requests.

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
		
        .. note:: 
            Attribute changes will only be published for
            changes due to some other entity.  They will not be published for changes made by the local API client.
            (This is done to prevent redundant notification for local changes)

        :param attr_name: The attribute to watch
        :param observer: The callback to invoke when change is detected
        """
        l = self.__observers.get(attr_name)
        if l is None:
            l = []
            self.__observers[attr_name] = l
        l.append(observer)

    def remove_attribute_observer(self, attr_name, observer):
        """
        Remove an observer.

        :param attr_name: the attribute to watch
        :param observer: the callback to invoke when change is detected
        """
        l = self.__observers.get(attr_name)
        if l is not None:
            l.remove(observer)
            if len(l) == 0:
                del self.__observers[attr_name]

    def notify_observers(self, attr_name):
        """
        (For subclass use only) Tell observers that the named attribute has changed.
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

    Most vehicle state is exposed through python attributes.  (i.e. ``vehicle.location``, etc.)  And most of these attributes are
    auto populated based on the capabilities of the particular autopilot we are talking to.

    Particular autopilots/vehicles may define different attributes from this standard list (extra batteries, GPIOs, etc.)
    However if a standard attribute is defined it must follow the rules specified below.

    To prevent name clashes the following naming convention should be used:
    ``ap_<name>`` - For autopilot specific parameters (apm 2.5, pixhawk etc...).  Example:
    ``user_<name>`` - For user specific parameters

    Standard attributes & types:

    ================= =======================================================
    Name              Type
    ================= =======================================================
    location          Location
    waypoint_home     Waypoint
    attitude          Attitude
    velocity          a three element list [ vx, vy, vz ] (in meter/sec)
    mode              VehicleMode
    airspeed          double
    groundspeed       double
    gps_0             GPSInfo
    battery_0_soc     double
    battery_0_volt    double
    armed             boolean
    channel_override  Dictionary (channelName -> value) (where channel name is 1,2,3, etc.)
    channel_readback  Dictionary (channelName -> value) (read only)
    ================= =======================================================

    .. todo:: FIXME: Should airspeed value move somewhere else from "Standard attributes & types" table?
	
    Autopilot specific attributes & types:

    ================= =======================================================
    Name              Type
    ================= =======================================================
    ap_pin5_mode      string (adc, dout, din)
    ap_pin5_value     double (0, 1, 2.3 etc...)
    ================= =======================================================

    **channel_override/channel_readback documentation:**
	
    The channel_override attribute takes a dictionary argument defining the channels to be overridden, and their new values. For example: ::

        the_vehicle.channel_override = { "1" : 900, "4" : 1000 }

    All multi-channel updates are atomic. Channels that are not specified in the dictionary are not overridden.		

    .. versionchanged:: 1.0
	
        This update replaces rc_override with channel_override/channel_readback documentation


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

    """

    def __init__(self):
        super(HasObservers,self).__init__()
        self.mavrx_callback = None

    @property
    def commands(self):
        """
        The (editable) waypoints for this vehicle.
        """
        None

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle.
        """
        return self._parameters

    def delete(self):
        """Delete this vehicle object.

        This requests deletion of the object on the server, this operation may throw an exception on failure (i.e. for
        local connections or insufficient user permissions).
        """
        pass

    def get_mission(self, query_params):
        """
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
        These message types are defined in the central MAVLink github repository.  For example, a Pixhawk understands
        the following messages: (from https://github.com/mavlink/mavlink/blob/master/message_definitions/v1.0/pixhawk.xml). 
		
        ::

          <message id="153" name="IMAGE_TRIGGER_CONTROL">
               <field type="uint8_t" name="enable">0 to disable, 1 to enable</field>
          </message>

        The name of the factory method will always be the lower case version of the message name with _encode appended.
        Each field in the xml message definition must be listed as arguments to this factory method.  So for this example
        message, the call would be:
		
        ::		

            msg = vehicle.message_factory.image_trigger_control_encode(True)
            vehicle.send_mavlink(msg)
        """
        None

    def send_mavlink(self, message):
        """
        This is an advanced/low-level method to send raw MAVLink to the vehicle.

        This method is included as an 'escape hatch' to allow developers to make progress if we've somehow missed providing
        some essential operation in the rest of this API.  Callers do not need to populate sysId/componentId/crc in the packet,
        this method will take care of that before sending.

        If you find yourself needing to use this mathod please contact the drone-platform google group and
        we'll see if we can support the operation you needed in some future revision of the API.

        :param: message: A MAVLink_message instance.  No need to fill in sysId/compId/seqNum - the API will take care of that.
        """
        pass

    def set_mavlink_callback(self, callback):
        """
        Provides asynchronous notification when any MAVLink packet is received from this vehicle.

        .. note:: 

            This method is implemented - but we hope you don't need it.
		
            Because of the async attribute/waypoint/parameter notifications there should be no need for
            API clients to see raw MAVLink.  Please provide feedback if we missed a use-case.
        """
        self.mavrx_callback = callback

    def flush(self):
        """
        It is important to understand that setting attributes/changing vehicle state may occur over a slow link.
		
        It is _not_ guaranteed that the effects of previous commands will be visible from reading vehicle attributes unless
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
    The set of named parameters for the vehicle.

    Attribute names are generated automatically based on parameter names.  Standard get/set operations can be performed.
    Operations are not guaranteed to be complete until :py:func:`flush() <Vehicle.flush>` is called on the parent :py:class:`Vehicle` object.
    """

class Command(mavutil.mavlink.MAVLink_mission_item_message):
    """
    A waypoint object.

    .. todo:: FIXME: Command class - for now we just inherit the standard MAVLink mission item contents.
    """
    pass

class CommandSequence(object):
    """
    A sequence of vehicle waypoints.

    Operations include 'array style' indexed access to the various contained Waypoints.
	
    Any changes by the client are not guaranteed to be complete until :py:func:`flush() <Vehicle.flush>` is called on the parent :py:class:`Vehicle` object.

    Waypoints are not downloaded from vehicle until :py:func:`download()` is called.  Fetch starts a (potentially asynchronous)
    waypoint download.  If you'd like to block your thread until the download is completed, call :py:func:`wait_valid()`. 
    """

    def download(self):
        '''Download all waypoints from the vehicle'''
        pass

    def wait_valid(self):
        '''Block the calling thread until waypoints have been downloaded'''
        pass

    def goto(self, location):
        '''
        Go to a specified Location

        (changing flight mode to GUIDED as necessary)
        '''
        pass

    def clear(self):
        '''Clears the command list'''
        pass

    def add(self, cmd):
        '''Add a new command at the end of the command list'''
        pass

    @property
    def count(self):
        '''return number of waypoints'''
        return 0

    @property
    def next(self):
        """
        Currently active waypoint number

        (implementation provided by subclass)
        """
        return None

    @next.setter
    def next(self, value):
        """
        Tell vehicle to change next waypoint

        (implementation provided by subclass)
        """
        pass


