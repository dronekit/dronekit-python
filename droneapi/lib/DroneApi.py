# DroneAPI module

def web_connect(authinfo):
    """
    Connect to the central dronehub server

    :param authinfo: A AuthInfo container (contains username, password, challenge info, etc...)
    """
    return APIConnection()

def local_connect():
    """
    Connect to the API provider for the local GCS (or vehicle if running on vehicle)
    """
    return APIConnection()

class AuthInfo(object):
    """
    Base class for various authentication flavors.
    Initially only simple username & password auth are supported
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

class ConnectionInfo(object):
    """
    Connection information for contacting the local vehicle
    """
    def __init__(self, mavproxy_options):
        self.maxproxy_options = mavproxy_options

class Attitude(object):
    """
    Attitude information

    FIXME, possibly repurpose/share with a standard python library
    """
    def __init__(self):
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0

class Point3D(object):
    """
    A location object -

    FIXME, possibly repurpose/share with a standard python library
    """
    pass

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

    This is the top level API connection returned from localConnect() or webConnect().  You should not manually create instances of
    this class.
    """

    def get_vehicles(self, query = None):
        """
        Find a set of vehicles that are controllable from this connection.

        :param query: This parameter will be documented with the web API, for now just use the default
        """
        #return [ Vehicle(), Vehicle() ]
        raise Exception("Subclasses must override")

class HasAttributeObservers(object):
    """
    Provides callback based notification on attribute changes.

    The argument list for observer is TBD but probably observer(attr_name, new_value).
    """
    def add_attribute_observer(self, attr_name, observer):
        """
        Add an observer.

        :param attr_name: the attribute to watch
        :param observer: the callback to invoke when change is detected
        """
        pass

    def remove_attribute_observer(self, attr_name, observer):
        """
        Remove an observer.

        :param attr_name: the attribute to watch
        :param observer: the callback to invoke when change is detected
        """
        pass

    def notify_observers(self, attr_name, new_value):
        """
        (For subclass use only) Tell observers that the named attribute has changed.

        FIXME would it make sense just to override __setattr__?
        """
        pass

class Vehicle(HasAttributeObservers):
    """
    The main vehicle API

    Asynchronous notification on change of vehicle state is available by registering observers (callbacks) for attribute or
    parameter changes.

    Most vehicle state is exposed through python attributes.  (i.e. vehicle.location, etc...)  And most of these attributes are
    auto populated based on the capabilities of the particular autopilot we are talking to.

    Particular autopilots/vehicles may define different attributes from this standard list (extra batteries, GPIOs, etc...)
    However if a standard attribute is defined it must follow the rules specified below.

    To prevent name clashes the following naming convention should be used:
    ap_<name> - For autopilot specific parameters (apm 2.5, pixhawk etc...).  Example:
    user_<name> - For user specific parameters

    Standard attributes & types:

    ================= =======================================================
    Name              Type
    ================= =======================================================
    location          Point3D
    waypoint_home     Waypoint
    attitude          Attitude
    mode              VehicleMode
    battery_0_soc     double
    battery_0_volt    double
    channel_override  Dictionary (channelName -> value) (formery rc_override)
    channel_readback  Dictionary (channelName -> value) (read only)
    ap_pin5_mode      string (adc, dout, din)
    ap_pin5_value     double (0, 1, 2.3 etc...)
    ================= =======================================================

    channel_override/channel_readback documentation:
    In the previous version of this API I used the 'tried and true'
    rc_override terminology.  However I've changed rc_override to be
    channel_override with a dictionary as the argument.
    (This idea is from @rmackay9 - thanks!)

    Strings will be defined per vehicle type ('pitch', 'yaw', 'roll' etc...)
    and rather than setting channel 3 to 1400 (for instance), you will pass
    in a dict with 'throttle':1200.  If you do not want to override particular
    channels, you should not populate them in the dictionary.

    It is worth noting by using a single dictionary it is guaranteed that all
    multi-channel changes are updated atomically.

    This change will be nice in two ways:

    * we can hide (eventually we can deprecate) any notion of rc channel
    numbers at all.
    * vehicles can eventually define new 'channels' for overridden values.

    Remaining FIXMEs:

    * FIXME - how to address the units issue?  Merely with documentation or some other way?
    * FIXME - is there any benefit of using lists rather than tuples for these attributes

    """

    def __init__(self):
        self._waypoints = CommandSequence()
        self._parameters = Parameters()

    @property
    def commands(self):
        """
        The (editable) waypoints for this vehicle.
        """
        return self._waypoints

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle.
        """
        return self._parameters

    def delete(self):
        """Delete this vehicle object.

        This requests deletion of the object on the server, this operation may throw an exception on failure (i.e. for
        local connections or insufficient user permissions)
        """
        pass

    def get_mission(self, query_params):
        """PLACEHOLDER

        Access to historical missions will not be included in the release 1 python API, they will only be accessible
        from the REST API.  (This is based on the most likely use-cases wanting a REST interface)

        :param query_params: Some TBD set of arguments that can be used to find a past mission
        :returns Mission -- the mission
        """
        return Mission()

    def send_mavlink(self, packet):
        """
        This is an advanced/low-level method to send raw mavlink to the vehicle.

        This method is included as an 'escape hatch' to allow developers to make progress if we've somehow missed providing
        some essentential operation in the rest of this API.  Callers do not need to populate sysId/componentId/crc in the packet,
        this method will take care of that before sending.

        If you find yourself needing to use this mathod please contact the drone-platform google group and
        we'll see if we can support the operation you needed in some future revision of the API.

        * FIXME: Instead of passing in bytes, probably better to have the developer pass in Mavlink packet objects.

        :param: packet: A mavlink packet.
        """
        pass

    def set_mavlink_callback(self, callback):
        """
        Provides asynchronous notification when any mavlink packet is received from this vehice.  FOR DISCUSSION!

        Note: I've included this prototype for feedback.  I _hope_ that it isn't necessary to provide this method as part
        of the API, because I think because of the async attribute/waypoint/parameter notifications there is no need for
        API clients to see raw mavlink.  Did I miss any use cases?  Feedback?

        If we do need to include this method it would be easy to implement.
        """
        pass

    def flush(self):
        """It is important to understand that setting attributes/changing vehicle state may occur over a slow link.
        It is _not_ guaranteed that the effects of previous commands will be visible from reading vehicle attributes unless
        flush() is called first.  After the return from flush any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects."""
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

    PLACEHOLDER - will not be included in the release 1 python API, they will only be accessible
    from the REST API.  (This is based on the most likely use-cases wanting a REST interface)"""
    pass

class Parameters(HasAttributeObservers):
    """
    The set of named parameters for the vehicle.

    Attribute names are generated automatically based on parameter names.  Standard get/set operations can be performed.
    Operations are not guaranteed to be complete until flush() is called on the parent Vehicle object.
    """

    def __getattr__(self, name):
        pass

    def __setattr__(self, name, value):
        pass

class Command(object):
    """
    A waypoint object.

    FIXME Documentation for Waypoint not included (yet).  But it will contain position, waypoint type and parameter arguments.
    """
    pass

class CommandSequence(object):
    """
    A sequence of vehicle waypoints.

    Documentation for Waypoints not included (yet).  Operations will include 'array style' indexed access to the various contained Waypoints.
    Any changes by the client are not guaranteed to be complete until flush() is called on the parent Vehicle object.
    """

    def __init__(self):
        self._next = None

    @property
    def next(self):
        """Currently active waypoint number"""
        return self._next

    @next.setter
    def next(self, value):
        """Tell vehicle to change next waypoint"""
        self._next = value


