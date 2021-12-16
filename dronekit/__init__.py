# DroneAPI module
"""
This is the API Reference for the DroneKit-Python API.

The main API is the :py:class:`Vehicle` class.
The code snippet below shows how to use :py:func:`connect` to obtain an instance of a connected vehicle:

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle using "connection string" (in this case an address on network)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

:py:class:`Vehicle` provides access to vehicle *state* through python attributes
(e.g. :py:attr:`Vehicle.mode`)
and to settings/parameters though the :py:attr:`Vehicle.parameters` attribute.
Asynchronous notification on vehicle attribute changes is available by registering listeners/observers.

Vehicle movement is primarily controlled using the :py:attr:`Vehicle.armed` attribute and
:py:func:`Vehicle.simple_takeoff` and :py:attr:`Vehicle.simple_goto` in GUIDED mode.

Velocity-based movement and control over other vehicle features can be achieved using custom MAVLink messages
(:py:func:`Vehicle.send_mavlink`, :py:func:`Vehicle.message_factory`).

It is also possible to work with vehicle "missions" using the :py:attr:`Vehicle.commands` attribute, and run them in AUTO mode.

All the logging is handled through the builtin Python `logging` module.

A number of other useful classes and methods are listed below.

----
"""

import sys
import collections

# Python3.10 removed MutableMapping from collections:
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping

import copy
import logging
import math
import struct
import time

import monotonic
from past.builtins import basestring

from pymavlink import mavutil, mavwp
from pymavlink.dialects.v10 import ardupilotmega

from dronekit.util import ErrprinterHandler


class APIException(Exception):
    """
    Base class for DroneKit related exceptions.

    :param String message: Message string describing the exception
    """


class TimeoutError(APIException):
    '''Raised by operations that have timeouts.'''


class Attitude(object):
    """
    Attitude information.

    An object of this type is returned by :py:attr:`Vehicle.attitude`.

    .. _figure_attitude:

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
        fmt = '{}:pitch={pitch},yaw={yaw},roll={roll}'
        return fmt.format(self.__class__.__name__, **vars(self))


class LocationGlobal(object):
    """
    A global location object.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
    The altitude is relative to mean sea-level (MSL).

    For example, a global location object with altitude 30 metres above sea level might be defined as:

    .. code:: python

       LocationGlobal(-34.364114, 149.166022, 30)

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the global frame.

    :param lat: Latitude.
    :param lon: Longitude.
    :param alt: Altitude in meters relative to mean sea-level (MSL).
    """

    def __init__(self, lat, lon, alt=None):
        self.lat = lat
        self.lon = lon
        self.alt = alt

        # This is for backward compatibility.
        self.local_frame = None
        self.global_frame = None

    def __str__(self):
        return "LocationGlobal:lat=%s,lon=%s,alt=%s" % (self.lat, self.lon, self.alt)


class LocationGlobalRelative(object):
    """
    A global location object, with attitude relative to home location altitude.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
    The altitude is relative to the *home position*.

    For example, a ``LocationGlobalRelative`` object with an altitude of 30 metres above the home location might be defined as:

    .. code:: python

       LocationGlobalRelative(-34.364114, 149.166022, 30)

    .. todo:: FIXME: Location class - possibly add a vector3 representation.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the global-relative frame.

    :param lat: Latitude.
    :param lon: Longitude.
    :param alt: Altitude in meters (relative to the home location).
    """

    def __init__(self, lat, lon, alt=None):
        self.lat = lat
        self.lon = lon
        self.alt = alt

        # This is for backward compatibility.
        self.local_frame = None
        self.global_frame = None

    def __str__(self):
        return "LocationGlobalRelative:lat=%s,lon=%s,alt=%s" % (self.lat, self.lon, self.alt)


class LocationLocal(object):
    """
    A local location object.

    The north, east and down are relative to the EKF origin.  This is most likely the location where the vehicle was turned on.

    An object of this type is owned by :py:attr:`Vehicle.location`. See that class for information on
    reading and observing location in the local frame.

    :param north: Position north of the EKF origin in meters.
    :param east: Position east of the EKF origin in meters.
    :param down: Position down from the EKF origin in meters. (i.e. negative altitude in meters)
    """

    def __init__(self, north, east, down):
        self.north = north
        self.east = east
        self.down = down

    def __str__(self):
        return "LocationLocal:north=%s,east=%s,down=%s" % (self.north, self.east, self.down)

    def distance_home(self):
        """
        Distance away from home, in meters. Returns 3D distance if `down` is known, otherwise 2D distance.
        """

        if self.north is not None and self.east is not None:
            if self.down is not None:
                return math.sqrt(self.north**2 + self.east**2 + self.down**2)
            else:
                return math.sqrt(self.north**2 + self.east**2)


class GPSInfo(object):
    """
    Standard information about GPS.

    If there is no GPS lock the parameters are set to ``None``.

    :param Int eph: GPS horizontal dilution of position (HDOP).
    :param Int epv: GPS vertical dilution of position (VDOP).
    :param Int fix_type: 0-1: no fix, 2: 2D fix, 3: 3D fix
    :param Int satellites_visible: Number of satellites visible.

    .. todo:: FIXME: GPSInfo class - possibly normalize eph/epv?  report fix type as string?
    """

    def __init__(self, eph, epv, fix_type, satellites_visible):
        self.eph = eph
        self.epv = epv
        self.fix_type = fix_type
        self.satellites_visible = satellites_visible

    def __str__(self):
        return "GPSInfo:fix=%s,num_sat=%s" % (self.fix_type, self.satellites_visible)


class Wind(object):
    """
    Wind information

    An object of this type is returned by :py:attr: `Vehicle.wind`.

    :param wind_direction: Wind direction in degrees
    :param wind_speed: Wind speed in m/s
    :param wind_speed_z: vertical wind speed in m/s
    """
    def __init__(self, wind_direction, wind_speed, wind_speed_z):
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.wind_speed_z = wind_speed_z
    
    def __str__(self):
        return "Wind: wind direction: {}, wind speed: {}, wind speed z: {}".format(self.wind_direction, self.wind_speed, self.wind_speed_z)


class Battery(object):
    """
    System battery information.

    An object of this type is returned by :py:attr:`Vehicle.battery`.

    :param voltage: Battery voltage in millivolts.
    :param current: Battery current, in 10 * milliamperes. ``None`` if the autopilot does not support current measurement.
    :param level: Remaining battery energy. ``None`` if the autopilot cannot estimate the remaining battery.
    """

    def __init__(self, voltage, current, level):
        self.voltage = voltage / 1000.0
        if current == -1:
            self.current = None
        else:
            self.current = current / 100.0
        if level == -1:
            self.level = None
        else:
            self.level = level

    def __str__(self):
        return "Battery:voltage={},current={},level={}".format(self.voltage, self.current,
                                                               self.level)


class Rangefinder(object):
    """
    Rangefinder readings.

    An object of this type is returned by :py:attr:`Vehicle.rangefinder`.

    :param distance: Distance (metres). ``None`` if the vehicle doesn't have a rangefinder.
    :param voltage: Voltage (volts). ``None`` if the vehicle doesn't have a rangefinder.
    """

    def __init__(self, distance, voltage):
        self.distance = distance
        self.voltage = voltage

    def __str__(self):
        return "Rangefinder: distance={}, voltage={}".format(self.distance, self.voltage)


class Version(object):
    """
    Autopilot version and type.

    An object of this type is returned by :py:attr:`Vehicle.version`.

    The version number can be read in a few different formats. To get it in a human-readable
    format, just print `vehicle.version`.  This might print something like "APM:Copter-3.3.2-rc4".

    .. versionadded:: 2.0.3

    .. py:attribute:: major

        Major version number (integer).

    .. py:attribute::minor

        Minor version number (integer).

    .. py:attribute:: patch

        Patch version number (integer).

    .. py:attribute:: release

        Release type (integer). See the enum `FIRMWARE_VERSION_TYPE <http://mavlink.org/messages/common#http://mavlink.org/messages/common#FIRMWARE_VERSION_TYPE_DEV>`_.

        This is a composite of the product release cycle stage (rc, beta etc) and the version in that cycle - e.g. 23.

    """
    def __init__(self, raw_version, autopilot_type, vehicle_type):
        self.autopilot_type = autopilot_type
        self.vehicle_type = vehicle_type
        self.raw_version = raw_version
        if raw_version is None:
            self.major = None
            self.minor = None
            self.patch = None
            self.release = None
        else:
            self.major   = raw_version >> 24 & 0xFF
            self.minor   = raw_version >> 16 & 0xFF
            self.patch   = raw_version >> 8  & 0xFF
            self.release = raw_version & 0xFF

    def is_stable(self):
        """
        Returns True if the autopilot reports that the current firmware is a stable
        release (not a pre-release or development version).
        """
        return self.release == 255

    def release_version(self):
        """
        Returns the version within the release type (an integer).
        This method returns "23" for Copter-3.3rc23.
        """
        if self.release is None:
            return None
        if self.release == 255:
            return 0
        return self.release % 64

    def release_type(self):
        """
        Returns text describing the release type e.g. "alpha", "stable" etc.
        """
        if self.release is None:
            return None
        types = ["dev", "alpha", "beta", "rc"]
        return types[self.release >> 6]

    def __str__(self):
        prefix = ""

        if self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA:
            prefix += "APM:"
        elif self.autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
            prefix += "PX4"
        else:
            prefix += "UnknownAutoPilot"

        if self.vehicle_type == mavutil.mavlink.MAV_TYPE_QUADROTOR:
            prefix += "Copter-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_FIXED_WING:
            prefix += "Plane-"
        elif self.vehicle_type == mavutil.mavlink.MAV_TYPE_GROUND_ROVER:
            prefix += "Rover-"
        else:
            prefix += "UnknownVehicleType%d-" % self.vehicle_type

        if self.release_type() is None:
            release_type = "UnknownReleaseType"
        elif self.is_stable():
            release_type = ""
        else:
            # e.g. "-rc23"
            release_type = "-" + str(self.release_type()) + str(self.release_version())

        return prefix + "%s.%s.%s" % (self.major, self.minor, self.patch) + release_type


class Capabilities:
    """
    Autopilot capabilities (supported message types and functionality).

    An object of this type is returned by :py:attr:`Vehicle.capabilities`.

    See the enum
    `MAV_PROTOCOL_CAPABILITY <http://mavlink.org/messages/common#MAV_PROTOCOL_CAPABILITY_MISSION_FLOAT>`_.

    .. versionadded:: 2.0.3


    .. py:attribute:: mission_float

        Autopilot supports MISSION float message type (Boolean).

    .. py:attribute:: param_float

        Autopilot supports the PARAM float message type (Boolean).

    .. py:attribute:: mission_int

        Autopilot supports MISSION_INT scaled integer message type (Boolean).

    .. py:attribute:: command_int

        Autopilot supports COMMAND_INT scaled integer message type (Boolean).

    .. py:attribute:: param_union

        Autopilot supports the PARAM_UNION message type (Boolean).

    .. py:attribute:: ftp

        Autopilot supports ftp for file transfers (Boolean).

    .. py:attribute:: set_attitude_target

        Autopilot supports commanding attitude offboard (Boolean).

    .. py:attribute:: set_attitude_target_local_ned

        Autopilot supports commanding position and velocity targets in local NED frame (Boolean).

    .. py:attribute:: set_altitude_target_global_int

        Autopilot supports commanding position and velocity targets in global scaled integers (Boolean).

    .. py:attribute:: terrain

        Autopilot supports terrain protocol / data handling (Boolean).

    .. py:attribute:: set_actuator_target

        Autopilot supports direct actuator control (Boolean).

    .. py:attribute:: flight_termination

        Autopilot supports the flight termination command (Boolean).

    .. py:attribute:: compass_calibration

        Autopilot supports onboard compass calibration (Boolean).
    """
    def __init__(self, capabilities):
        self.mission_float                  = (((capabilities >> 0)  & 1) == 1)
        self.param_float                    = (((capabilities >> 1)  & 1) == 1)
        self.mission_int                    = (((capabilities >> 2)  & 1) == 1)
        self.command_int                    = (((capabilities >> 3)  & 1) == 1)
        self.param_union                    = (((capabilities >> 4)  & 1) == 1)
        self.ftp                            = (((capabilities >> 5)  & 1) == 1)
        self.set_attitude_target            = (((capabilities >> 6)  & 1) == 1)
        self.set_attitude_target_local_ned  = (((capabilities >> 7)  & 1) == 1)
        self.set_altitude_target_global_int = (((capabilities >> 8)  & 1) == 1)
        self.terrain                        = (((capabilities >> 9)  & 1) == 1)
        self.set_actuator_target            = (((capabilities >> 10) & 1) == 1)
        self.flight_termination             = (((capabilities >> 11) & 1) == 1)
        self.compass_calibration            = (((capabilities >> 12) & 1) == 1)


class VehicleMode(object):
    """
    This object is used to get and set the current "flight mode".

    The flight mode determines the behaviour of the vehicle and what commands it can obey.
    The recommended flight modes for *DroneKit-Python* apps depend on the vehicle type:

    * Copter apps should use ``AUTO`` mode for "normal" waypoint missions and ``GUIDED`` mode otherwise.
    * Plane and Rover apps should use the ``AUTO`` mode in all cases, re-writing the mission commands if "dynamic"
      behaviour is required (they support only a limited subset of commands in ``GUIDED`` mode).
    * Some modes like ``RETURN_TO_LAUNCH`` can be used on all platforms. Care should be taken
      when using manual modes as these may require remote control input from the user.

    The available set of supported flight modes is vehicle-specific (see
    `Copter Modes <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/>`_,
    `Plane Modes <http://plane.ardupilot.com/wiki/flying/flight-modes/>`_,
    `Rover Modes <http://rover.ardupilot.com/wiki/configuration-2/#mode_meanings>`_). If an unsupported mode is set the script
    will raise a ``KeyError`` exception.

    The :py:attr:`Vehicle.mode` attribute can be queried for the current mode.
    The code snippet below shows how to observe changes to the mode and then read the value:

    .. code:: python

        #Callback definition for mode observer
        def mode_callback(self, attr_name):
            print "Vehicle Mode", self.mode

        #Add observer callback for attribute `mode`
        vehicle.add_attribute_listener('mode', mode_callback)

    The code snippet below shows how to change the vehicle mode to AUTO:

    .. code:: python

        # Set the vehicle into auto mode
        vehicle.mode = VehicleMode("AUTO")

    For more information on getting/setting/observing the :py:attr:`Vehicle.mode`
    (and other attributes) see the :ref:`attributes guide <vehicle_state_attributes>`.

    .. py:attribute:: name

        The mode name, as a ``string``.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "VehicleMode:%s" % self.name

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other


class SystemStatus(object):
    """
    This object is used to get and set the current "system status".

    An object of this type is returned by :py:attr:`Vehicle.system_status`.

    .. py:attribute:: state

        The system state, as a ``string``.
    """

    def __init__(self, state):
        self.state = state

    def __str__(self):
        return "SystemStatus:%s" % self.state

    def __eq__(self, other):
        return self.state == other

    def __ne__(self, other):
        return self.state != other


class HasObservers(object):
    def __init__(self):
        logging.basicConfig()
        self._logger = logging.getLogger(__name__)

        # A mapping from attr_name to a list of observers
        self._attribute_listeners = {}
        self._attribute_cache = {}

    def add_attribute_listener(self, attr_name, observer):
        """
        Add an attribute listener callback.

        The callback function (``observer``) is invoked differently depending on the *type of attribute*.
        Attributes that represent sensor values or which are used to monitor connection status are updated
        whenever a message is received from the vehicle. Attributes which reflect vehicle "state" are
        only updated when their values change (for example :py:attr:`Vehicle.system_status`,
        :py:attr:`Vehicle.armed`, and :py:attr:`Vehicle.mode`).

        The callback can be removed using :py:func:`remove_attribute_listener`.

        .. note::

            The :py:func:`on_attribute` decorator performs the same operation as this method, but with
            a more elegant syntax. Use ``add_attribute_listener`` by preference if you will need to remove
            the observer.

        The argument list for the callback is ``observer(object, attr_name, attribute_value)``:

        * ``self`` - the associated :py:class:`Vehicle`. This may be compared to a global vehicle handle
          to implement vehicle-specific callback handling (if needed).
        * ``attr_name`` - the attribute name. This can be used to infer which attribute has triggered
          if the same callback is used for watching several attributes.
        * ``value`` - the attribute value (so you don't need to re-query the vehicle object).

        The example below shows how to get callbacks for (global) location changes:

        .. code:: python

            #Callback to print the location in global frame
            def location_callback(self, attr_name, msg):
                print "Location (Global): ", msg

            #Add observer for the vehicle's current location
            vehicle.add_attribute_listener('global_frame', location_callback)

        See :ref:`vehicle_state_observe_attributes` for more information.

        :param String attr_name: The name of the attribute to watch (or '*' to watch all attributes).
        :param observer: The callback to invoke when a change in the attribute is detected.

        """
        listeners_for_attr = self._attribute_listeners.get(attr_name)
        if listeners_for_attr is None:
            listeners_for_attr = []
            self._attribute_listeners[attr_name] = listeners_for_attr
        if observer not in listeners_for_attr:
            listeners_for_attr.append(observer)

    def remove_attribute_listener(self, attr_name, observer):
        """
        Remove an attribute listener (observer) that was previously added using :py:func:`add_attribute_listener`.

        For example, the following line would remove a previously added vehicle 'global_frame'
        observer called ``location_callback``:

        .. code:: python

            vehicle.remove_attribute_listener('global_frame', location_callback)

        See :ref:`vehicle_state_observe_attributes` for more information.

        :param String attr_name: The attribute name that is to have an observer removed (or '*' to remove an 'all attribute' observer).
        :param observer: The callback function to remove.

        """
        listeners_for_attr = self._attribute_listeners.get(attr_name)
        if listeners_for_attr is not None:
            listeners_for_attr.remove(observer)
            if len(listeners_for_attr) == 0:
                del self._attribute_listeners[attr_name]

    def notify_attribute_listeners(self, attr_name, value, cache=False):
        """
        This method is used to update attribute observers when the named attribute is updated.

        You should call it in your message listeners after updating an attribute with
        information from a vehicle message.

        By default the value of ``cache`` is ``False`` and every update from the vehicle is sent to listeners
        (whether or not the attribute has changed).  This is appropriate for attributes which represent sensor
        or heartbeat-type monitoring.

        Set ``cache=True`` to update listeners only when the value actually changes (cache the previous
        attribute value). This should be used where clients will only ever need to know the value when it has
        changed. For example, this setting has been used for notifying :py:attr:`mode` changes.

        See :ref:`example_create_attribute` for more information.

        :param String attr_name: The name of the attribute that has been updated.
        :param value: The current value of the attribute that has been updated.
        :param Boolean cache: Set ``True`` to only notify observers when the attribute value changes.
        """
        # Cached values are not re-sent if they are unchanged.
        if cache:
            if self._attribute_cache.get(attr_name) == value:
                return
            self._attribute_cache[attr_name] = value

        # Notify observers.
        for fn in self._attribute_listeners.get(attr_name, []):
            try:
                fn(self, attr_name, value)
            except Exception:
                self._logger.exception('Exception in attribute handler for %s' % attr_name, exc_info=True)

        for fn in self._attribute_listeners.get('*', []):
            try:
                fn(self, attr_name, value)
            except Exception:
                self._logger.exception('Exception in attribute handler for %s' % attr_name, exc_info=True)

    def on_attribute(self, name):
        """
        Decorator for attribute listeners.

        The decorated function (``observer``) is invoked differently depending on the *type of attribute*.
        Attributes that represent sensor values or which are used to monitor connection status are updated
        whenever a message is received from the vehicle. Attributes which reflect vehicle "state" are
        only updated when their values change (for example :py:func:`Vehicle.system_status`,
        :py:attr:`Vehicle.armed`, and :py:attr:`Vehicle.mode`).

        The argument list for the callback is ``observer(object, attr_name, attribute_value)``

        * ``self`` - the associated :py:class:`Vehicle`. This may be compared to a global vehicle handle
          to implement vehicle-specific callback handling (if needed).
        * ``attr_name`` - the attribute name. This can be used to infer which attribute has triggered
          if the same callback is used for watching several attributes.
        * ``msg`` - the attribute value (so you don't need to re-query the vehicle object).

        .. note::

            There is no way to remove an attribute listener added with this decorator. Use
            :py:func:`add_attribute_listener` if you need to be able to remove
            the :py:func:`attribute listener <remove_attribute_listener>`.

        The code fragment below shows how you can create a listener for the attitude attribute.

        .. code:: python

            @vehicle.on_attribute('attitude')
            def attitude_listener(self, name, msg):
                print '%s attribute is: %s' % (name, msg)

        See :ref:`vehicle_state_observe_attributes` for more information.

        :param String name: The name of the attribute to watch (or '*' to watch all attributes).
        :param observer: The callback to invoke when a change in the attribute is detected.
        """

        def decorator(fn):
            if isinstance(name, list):
                for n in name:
                    self.add_attribute_listener(n, fn)
            else:
                self.add_attribute_listener(name, fn)

        return decorator


class ChannelsOverride(dict):
    """
    A dictionary class for managing Vehicle channel overrides.

    Channels can be read, written, or cleared by index or using a dictionary syntax.
    To clear a value, set it to ``None`` or use ``del`` on the item.

    An object of this type is returned by :py:attr:`Vehicle.channels.overrides <Channels.overrides>`.

    For more information and examples see :ref:`example_channel_overrides`.
    """

    def __init__(self, vehicle):
        self._vehicle = vehicle
        self._count = 8  # Fixed by MAVLink
        self._active = True

    def __getitem__(self, key):
        return dict.__getitem__(self, str(key))

    def __setitem__(self, key, value):
        if not (0 < int(key) <= self._count):
            raise KeyError('Invalid channel index %s' % key)
        if not value:
            try:
                dict.__delitem__(self, str(key))
            except:
                pass
        else:
            dict.__setitem__(self, str(key), value)
        self._send()

    def __delitem__(self, key):
        dict.__delitem__(self, str(key))
        self._send()

    def __len__(self):
        return self._count

    def _send(self):
        if self._active:
            overrides = [0] * 8
            for k, v in self.items():
                overrides[int(k) - 1] = v
            self._vehicle._master.mav.rc_channels_override_send(0, 0, *overrides)


class Channels(dict):
    """
    A dictionary class for managing RC channel information associated with a :py:class:`Vehicle`.

    An object of this type is accessed through :py:attr:`Vehicle.channels`. This object also stores
    the current vehicle channel overrides through its :py:attr:`overrides` attribute.

    For more information and examples see :ref:`example_channel_overrides`.
    """

    def __init__(self, vehicle, count):
        self._vehicle = vehicle
        self._count = count
        self._overrides = ChannelsOverride(vehicle)

        # populate readback
        self._readonly = False
        for k in range(0, count):
            self[k + 1] = None
        self._readonly = True

    @property
    def count(self):
        """
        The number of channels defined in the dictionary (currently 8).
        """
        return self._count

    def __getitem__(self, key):
        return dict.__getitem__(self, str(key))

    def __setitem__(self, key, value):
        if self._readonly:
            raise TypeError('__setitem__ is not supported on Channels object')
        return dict.__setitem__(self, str(key), value)

    def __len__(self):
        return self._count

    def _update_channel(self, channel, value):
        # If we have channels on different ports, we expand the Channels
        # object to support them.
        channel = int(channel)
        self._readonly = False
        self[channel] = value
        self._readonly = True
        self._count = max(self._count, channel)

    @property
    def overrides(self):
        """
        Attribute to read, set and clear channel overrides (also known as "rc overrides")
        associated with a :py:class:`Vehicle` (via :py:class:`Vehicle.channels`). This is an
        object of type :py:class:`ChannelsOverride`.

        For more information and examples see :ref:`example_channel_overrides`.

        To set channel overrides:

        .. code:: python

            # Set and clear overrids using dictionary syntax (clear by setting override to none)
            vehicle.channels.overrides = {'5':None, '6':None,'3':500}

            # You can also set and clear overrides using indexing syntax
            vehicle.channels.overrides['2'] = 200
            vehicle.channels.overrides['2'] = None

            # Clear using 'del'
            del vehicle.channels.overrides['3']

            # Clear all overrides by setting an empty dictionary
            vehicle.channels.overrides = {}

        Read the channel overrides either as a dictionary or by index. Note that you'll get
        a ``KeyError`` exception if you read a channel override that has not been set.

        .. code:: python

            # Get all channel overrides
            print " Channel overrides: %s" % vehicle.channels.overrides
            # Print just one channel override
            print " Ch2 override: %s" % vehicle.channels.overrides['2']
        """
        return self._overrides

    @overrides.setter
    def overrides(self, newch):
        self._overrides._active = False
        self._overrides.clear()
        for k, v in newch.items():
            if v:
                self._overrides[str(k)] = v
            else:
                try:
                    del self._overrides[str(k)]
                except:
                    pass
        self._overrides._active = True
        self._overrides._send()


class Locations(HasObservers):
    """
    An object for holding location information in global, global relative and local frames.

    :py:class:`Vehicle` owns an object of this type. See :py:attr:`Vehicle.location` for information on
    reading and observing location in the different frames.

    The different frames are accessed through the members, which are created with this object.
    They can be read, and are observable.
    """

    def __init__(self, vehicle):
        super(Locations, self).__init__()

        self._lat = None
        self._lon = None
        self._alt = None
        self._relative_alt = None

        @vehicle.on_message('GLOBAL_POSITION_INT')
        def listener(vehicle, name, m):
            (self._lat, self._lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            self._relative_alt = m.relative_alt / 1000.0
            self.notify_attribute_listeners('global_relative_frame', self.global_relative_frame)
            vehicle.notify_attribute_listeners('location.global_relative_frame',
                                               vehicle.location.global_relative_frame)

            if self._alt is not None or m.alt != 0:
                # Require first alt value to be non-0
                # TODO is this the proper check to do?
                self._alt = m.alt / 1000.0
                self.notify_attribute_listeners('global_frame', self.global_frame)
                vehicle.notify_attribute_listeners('location.global_frame',
                                                   vehicle.location.global_frame)

            vehicle.notify_attribute_listeners('location', vehicle.location)

        self._north = None
        self._east = None
        self._down = None

        @vehicle.on_message('LOCAL_POSITION_NED')
        def listener(vehicle, name, m):
            self._north = m.x
            self._east = m.y
            self._down = m.z
            self.notify_attribute_listeners('local_frame', self.local_frame)
            vehicle.notify_attribute_listeners('location.local_frame', vehicle.location.local_frame)
            vehicle.notify_attribute_listeners('location', vehicle.location)

    @property
    def local_frame(self):
        """
        Location in local NED frame (a :py:class:`LocationGlobalRelative`).

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Local Location: %s" % vehicle.location.local_frame

        This location will not start to update until the vehicle is armed.
        """
        return LocationLocal(self._north, self._east, self._down)

    @property
    def global_frame(self):
        """
        Location in global frame (a :py:class:`LocationGlobal`).

        The latitude and longitude are relative to the
        `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
        The altitude is relative to mean sea-level (MSL).

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Global Location: %s" % vehicle.location.global_frame
            print "Sea level altitude is: %s" % vehicle.location.global_frame.alt

        Its ``lat`` and ``lon`` attributes are populated shortly after GPS becomes available.
        The ``alt`` can take several seconds longer to populate (from the barometer).
        Listeners are not notified of changes to this attribute until it has fully populated.

        To watch for changes you can use :py:func:`Vehicle.on_attribute` decorator or
        :py:func:`add_attribute_listener` (decorator approach shown below):

        .. code-block:: python

            @vehicle.on_attribute('location.global_frame')
            def listener(self, attr_name, value):
                print " Global: %s" % value

            #Alternatively, use decorator: ``@vehicle.location.on_attribute('global_frame')``.
        """
        return LocationGlobal(self._lat, self._lon, self._alt)

    @property
    def global_relative_frame(self):
        """
        Location in global frame, with altitude relative to the home location
        (a :py:class:`LocationGlobalRelative`).

        The latitude and longitude are relative to the
        `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
        The altitude is relative to :py:attr:`home location <Vehicle.home_location>`.

        This is accessed through the :py:attr:`Vehicle.location` attribute:

        .. code-block:: python

            print "Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
            print "Altitude relative to home_location: %s" % vehicle.location.global_relative_frame.alt
        """
        return LocationGlobalRelative(self._lat, self._lon, self._relative_alt)


class Vehicle(HasObservers):
    """
    The main vehicle API.

    Vehicle state is exposed through 'attributes' (e.g. :py:attr:`heading`). All attributes can be
    read, and some are also settable
    (:py:attr:`mode`, :py:attr:`armed` and :py:attr:`home_location`).

    Attributes can also be asynchronously monitored for changes by registering listener callback
    functions.

    Vehicle "settings" (parameters) are read/set using the :py:attr:`parameters` attribute.
    Parameters can be iterated and are also individually observable.

    Vehicle movement is primarily controlled using the :py:attr:`armed` attribute and
    :py:func:`simple_takeoff` and :py:func:`simple_goto` in GUIDED mode.

    It is also possible to work with vehicle "missions" using the :py:attr:`commands` attribute,
    and run them in AUTO mode.

    STATUSTEXT log messages from the autopilot are handled through a separate logger.
    It is possible to configure the log level, the formatting, etc. by accessing the logger, e.g.:

    .. code-block:: python

        import logging
        autopilot_logger = logging.getLogger('autopilot')
        autopilot_logger.setLevel(logging.DEBUG)

    The guide contains more detailed information on the different ways you can use
    the ``Vehicle`` class:

    - :doc:`guide/vehicle_state_and_parameters`
    - :doc:`guide/copter/guided_mode`
    - :doc:`guide/auto_mode`


    .. note::

        This class currently exposes just the attributes that are most commonly used by all
        vehicle types. if you need to add additional attributes then subclass ``Vehicle``
        as demonstrated in :doc:`examples/create_attribute`.

        Please then :doc:`contribute <contributing/contributions_api>` your additions back
        to the project!
    """

    def __init__(self, handler):
        super(Vehicle, self).__init__()

        self._logger = logging.getLogger(__name__)  # Logger for DroneKit
        self._autopilot_logger = logging.getLogger('autopilot')  # Logger for the autopilot messages
        # MAVLink-to-logging-module log severity mappings
        self._mavlink_statustext_severity = {
            0: logging.CRITICAL,
            1: logging.CRITICAL,
            2: logging.CRITICAL,
            3: logging.ERROR,
            4: logging.WARNING,
            5: logging.INFO,
            6: logging.INFO,
            7: logging.DEBUG
        }

        self._handler = handler
        self._master = handler.master

        # Cache all updated attributes for wait_ready.
        # By default, we presume all "commands" are loaded.
        self._ready_attrs = {'commands'}

        # Default parameters when calling wait_ready() or wait_ready(True).
        self._default_ready_attrs = ['parameters', 'gps_0', 'armed', 'mode', 'attitude']

        @self.on_attribute('*')
        def listener(_, name, value):
            self._ready_attrs.add(name)

        # Attaches message listeners.
        self._message_listeners = dict()

        @handler.forward_message
        def listener(_, msg):
            self.notify_message_listeners(msg.get_type(), msg)

        self._location = Locations(self)
        self._vx = None
        self._vy = None
        self._vz = None


        self._wind_direction = None
        self._wind_speed = None
        self._wind_speed_z = None

        @self.on_message('WIND')
        def listener(self,name, m):
            """ WIND {direction : -180.0, speed : 0.0, speed_z : 0.0} """
            self._wind_direction = m.direction
            self._wind_speed = m.speed
            self._wind_speed_z = m.speed_z


        @self.on_message('STATUSTEXT')
        def statustext_listener(self, name, m):
            # Log the STATUSTEXT on the autopilot logger, with the correct severity
            self._autopilot_logger.log(
                msg=m.text.strip(),
                level=self._mavlink_statustext_severity[m.severity]
            )

        @self.on_message('GLOBAL_POSITION_INT')
        def listener(self, name, m):
            (self._vx, self._vy, self._vz) = (m.vx / 100.0, m.vy / 100.0, m.vz / 100.0)
            self.notify_attribute_listeners('velocity', self.velocity)

        self._pitch = None
        self._yaw = None
        self._roll = None
        self._pitchspeed = None
        self._yawspeed = None
        self._rollspeed = None

        @self.on_message('ATTITUDE')
        def listener(self, name, m):
            self._pitch = m.pitch
            self._yaw = m.yaw
            self._roll = m.roll
            self._pitchspeed = m.pitchspeed
            self._yawspeed = m.yawspeed
            self._rollspeed = m.rollspeed
            self.notify_attribute_listeners('attitude', self.attitude)

        self._heading = None
        self._airspeed = None
        self._groundspeed = None

        @self.on_message('VFR_HUD')
        def listener(self, name, m):
            self._heading = m.heading
            self.notify_attribute_listeners('heading', self.heading)
            self._airspeed = m.airspeed
            self.notify_attribute_listeners('airspeed', self.airspeed)
            self._groundspeed = m.groundspeed
            self.notify_attribute_listeners('groundspeed', self.groundspeed)

        self._rngfnd_distance = None
        self._rngfnd_voltage = None

        @self.on_message('RANGEFINDER')
        def listener(self, name, m):
            self._rngfnd_distance = m.distance
            self._rngfnd_voltage = m.voltage
            self.notify_attribute_listeners('rangefinder', self.rangefinder)

        self._mount_pitch = None
        self._mount_yaw = None
        self._mount_roll = None

        @self.on_message('MOUNT_STATUS')
        def listener(self, name, m):
            self._mount_pitch = m.pointing_a / 100.0
            self._mount_roll = m.pointing_b / 100.0
            self._mount_yaw = m.pointing_c / 100.0
            self.notify_attribute_listeners('mount', self.mount_status)

        self._capabilities = None
        self._raw_version = None
        self._autopilot_version_msg_count = 0

        @self.on_message('AUTOPILOT_VERSION')
        def listener(vehicle, name, m):
            self._capabilities = m.capabilities
            self._raw_version = m.flight_sw_version
            self._autopilot_version_msg_count += 1
            if self._capabilities != 0 or self._autopilot_version_msg_count > 5:
                # ArduPilot <3.4 fails to send capabilities correctly
                # straight after boot, and even older versions send
                # this back as always-0.
                vehicle.remove_message_listener('HEARTBEAT', self.send_capabilities_request)
            self.notify_attribute_listeners('autopilot_version', self._raw_version)

        # gimbal
        self._gimbal = Gimbal(self)

        # All keys are strings.
        self._channels = Channels(self, 8)

        @self.on_message(['RC_CHANNELS_RAW', 'RC_CHANNELS'])
        def listener(self, name, m):
            def set_rc(chnum, v):
                '''Private utility for handling rc channel messages'''
                # use port to allow ch nums greater than 8
                port = 0 if name == "RC_CHANNELS" else m.port
                self._channels._update_channel(str(port * 8 + chnum), v)

            for i in range(1, (18 if name == "RC_CHANNELS" else 8)+1):
                set_rc(i, getattr(m, "chan{}_raw".format(i)))

            self.notify_attribute_listeners('channels', self.channels)

        self._voltage = None
        self._current = None
        self._level = None

        @self.on_message('SYS_STATUS')
        def listener(self, name, m):
            self._voltage = m.voltage_battery
            self._current = m.current_battery
            self._level = m.battery_remaining
            self.notify_attribute_listeners('battery', self.battery)

        self._eph = None
        self._epv = None
        self._satellites_visible = None
        self._fix_type = None  # FIXME support multiple GPSs per vehicle - possibly by using componentId

        @self.on_message('GPS_RAW_INT')
        def listener(self, name, m):
            self._eph = m.eph
            self._epv = m.epv
            self._satellites_visible = m.satellites_visible
            self._fix_type = m.fix_type
            self.notify_attribute_listeners('gps_0', self.gps_0)

        self._current_waypoint = 0

        @self.on_message(['WAYPOINT_CURRENT', 'MISSION_CURRENT'])
        def listener(self, name, m):
            self._current_waypoint = m.seq

        self._ekf_poshorizabs = False
        self._ekf_constposmode = False
        self._ekf_predposhorizabs = False

        @self.on_message('EKF_STATUS_REPORT')
        def listener(self, name, m):
            # boolean: EKF's horizontal position (absolute) estimate is good
            self._ekf_poshorizabs = (m.flags & ardupilotmega.EKF_POS_HORIZ_ABS) > 0
            # boolean: EKF is in constant position mode and does not know it's absolute or relative position
            self._ekf_constposmode = (m.flags & ardupilotmega.EKF_CONST_POS_MODE) > 0
            # boolean: EKF's predicted horizontal position (absolute) estimate is good
            self._ekf_predposhorizabs = (m.flags & ardupilotmega.EKF_PRED_POS_HORIZ_ABS) > 0

            self.notify_attribute_listeners('ekf_ok', self.ekf_ok, cache=True)

        self._flightmode = 'AUTO'
        self._armed = False
        self._system_status = None
        self._autopilot_type = None  # PX4, ArduPilot, etc.
        self._vehicle_type = None  # quadcopter, plane, etc.

        @self.on_message('HEARTBEAT')
        def listener(self, name, m):
            # ignore groundstations
            if m.type == mavutil.mavlink.MAV_TYPE_GCS:
                return
            self._armed = (m.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            self.notify_attribute_listeners('armed', self.armed, cache=True)
            self._autopilot_type = m.autopilot
            self._vehicle_type = m.type
            if self._is_mode_available(m.custom_mode, m.base_mode) is False:
                raise APIException("mode (%s, %s) not available on mavlink definition" % (m.custom_mode, m.base_mode))
            if self._autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
                self._flightmode = mavutil.interpret_px4_mode(m.base_mode, m.custom_mode)
            else:
                self._flightmode = self._mode_mapping_bynumber[m.custom_mode]
            self.notify_attribute_listeners('mode', self.mode, cache=True)
            self._system_status = m.system_status
            self.notify_attribute_listeners('system_status', self.system_status, cache=True)

        # Waypoints.

        self._home_location = None
        self._wploader = mavwp.MAVWPLoader()
        self._wp_loaded = True
        self._wp_uploaded = None
        self._wpts_dirty = False
        self._commands = CommandSequence(self)

        @self.on_message(['WAYPOINT_COUNT', 'MISSION_COUNT'])
        def listener(self, name, msg):
            if not self._wp_loaded:
                self._wploader.clear()
                self._wploader.expected_count = msg.count
                self._master.waypoint_request_send(0)

        @self.on_message(['HOME_POSITION'])
        def listener(self, name, msg):
            self._home_location = LocationGlobal(msg.latitude / 1.0e7, msg.longitude / 1.0e7, msg.altitude / 1000.0)
            self.notify_attribute_listeners('home_location', self.home_location, cache=True)

        @self.on_message(['WAYPOINT', 'MISSION_ITEM'])
        def listener(self, name, msg):
            if not self._wp_loaded:
                if msg.seq == 0:
                    if not (msg.x == 0 and msg.y == 0 and msg.z == 0):
                        self._home_location = LocationGlobal(msg.x, msg.y, msg.z)

                if msg.seq > self._wploader.count():
                    # Unexpected waypoint
                    pass
                elif msg.seq < self._wploader.count():
                    # Waypoint duplicate
                    pass
                else:
                    self._wploader.add(msg)

                    if msg.seq + 1 < self._wploader.expected_count:
                        self._master.waypoint_request_send(msg.seq + 1)
                    else:
                        self._wp_loaded = True
                        self.notify_attribute_listeners('commands', self.commands)

        # Waypoint send to master
        @self.on_message(['WAYPOINT_REQUEST', 'MISSION_REQUEST'])
        def listener(self, name, msg):
            if self._wp_uploaded is not None:
                wp = self._wploader.wp(msg.seq)
                handler.fix_targets(wp)
                self._master.mav.send(wp)
                self._wp_uploaded[msg.seq] = True

        # TODO: Waypoint loop listeners

        # Parameters.

        start_duration = 0.2
        repeat_duration = 1

        self._params_count = -1
        self._params_set = []
        self._params_loaded = False
        self._params_start = False
        self._params_map = {}
        self._params_last = monotonic.monotonic()  # Last new param.
        self._params_duration = start_duration
        self._parameters = Parameters(self)

        @handler.forward_loop
        def listener(_):
            # Check the time duration for last "new" params exceeds watchdog.
            if not self._params_start:
                return

            if not self._params_loaded and all(x is not None for x in self._params_set):
                self._params_loaded = True
                self.notify_attribute_listeners('parameters', self.parameters)

            if not self._params_loaded and monotonic.monotonic() - self._params_last > self._params_duration:
                c = 0
                for i, v in enumerate(self._params_set):
                    if v is None:
                        self._master.mav.param_request_read_send(0, 0, b'', i)
                        c += 1
                        if c > 50:
                            break
                self._params_duration = repeat_duration
                self._params_last = monotonic.monotonic()

        @self.on_message(['PARAM_VALUE'])
        def listener(self, name, msg):
            # If we discover a new param count, assume we
            # are receiving a new param set.
            if self._params_count != msg.param_count:
                self._params_loaded = False
                self._params_start = True
                self._params_count = msg.param_count
                self._params_set = [None] * msg.param_count

            # Attempt to set the params. We throw an error
            # if the index is out of range of the count or
            # we lack a param_id.
            try:
                if msg.param_index < msg.param_count and msg:
                    if self._params_set[msg.param_index] is None:
                        self._params_last = monotonic.monotonic()
                        self._params_duration = start_duration
                    self._params_set[msg.param_index] = msg

                self._params_map[msg.param_id] = msg.param_value
                self._parameters.notify_attribute_listeners(msg.param_id, msg.param_value,
                                                            cache=True)
            except:
                import traceback
                traceback.print_exc()

        # Heartbeats.

        self._heartbeat_started = False
        self._heartbeat_lastsent = 0
        self._heartbeat_lastreceived = 0
        self._heartbeat_timeout = False

        self._heartbeat_warning = 5
        self._heartbeat_error = 30
        self._heartbeat_system = None

        @handler.forward_loop
        def listener(_):
            # Send 1 heartbeat per second
            if monotonic.monotonic() - self._heartbeat_lastsent > 1:
                self._master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
                                                mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                self._heartbeat_lastsent = monotonic.monotonic()

            # Timeouts.
            if self._heartbeat_started:
                if self._heartbeat_error and monotonic.monotonic() - self._heartbeat_lastreceived > self._heartbeat_error > 0:
                    raise APIException('No heartbeat in %s seconds, aborting.' %
                                       self._heartbeat_error)
                elif monotonic.monotonic() - self._heartbeat_lastreceived > self._heartbeat_warning:
                    if self._heartbeat_timeout is False:
                        self._logger.warning('Link timeout, no heartbeat in last %s seconds' % self._heartbeat_warning)
                        self._heartbeat_timeout = True

        @self.on_message(['HEARTBEAT'])
        def listener(self, name, msg):
            # ignore groundstations
            if msg.type == mavutil.mavlink.MAV_TYPE_GCS:
                return
            self._heartbeat_system = msg.get_srcSystem()
            self._heartbeat_lastreceived = monotonic.monotonic()
            if self._heartbeat_timeout:
                self._logger.info('...link restored.')
            self._heartbeat_timeout = False

        self._last_heartbeat = None

        @handler.forward_loop
        def listener(_):
            if self._heartbeat_lastreceived:
                self._last_heartbeat = monotonic.monotonic() - self._heartbeat_lastreceived
                self.notify_attribute_listeners('last_heartbeat', self.last_heartbeat)

    @property
    def last_heartbeat(self):
        """
        Time since last MAVLink heartbeat was received (in seconds).

        The attribute can be used to monitor link activity and implement script-specific timeout handling.

        For example, to pause the script if no heartbeat is received for more than 1 second you might implement
        the following observer, and use ``pause_script`` in a program loop to wait until the link is recovered:

        .. code-block:: python

            pause_script=False

            @vehicle.on_attribute('last_heartbeat')
            def listener(self, attr_name, value):
                global pause_script
                if value > 1 and not pause_script:
                    print "Pausing script due to bad link"
                    pause_script=True;
                if value < 1 and pause_script:
                    pause_script=False;
                    print "Un-pausing script"

        The observer will be called at the period of the messaging loop (about every 0.01 seconds). Testing
        on SITL indicates that ``last_heartbeat`` averages about .5 seconds, but will rarely exceed 1.5 seconds
        when connected. Whether heartbeat monitoring can be useful will very much depend on the application.


        .. note::

            If you just want to change the heartbeat timeout you can modify the ``heartbeat_timeout``
            parameter passed to the :py:func:`connect() <dronekit.connect>` function.

        """
        return self._last_heartbeat

    def on_message(self, name):
        """
        Decorator for message listener callback functions.

        .. tip::

            This is the most elegant way to define message listener callback functions.
            Use :py:func:`add_message_listener` only if you need to be able to
            :py:func:`remove the listener <remove_message_listener>` later.

        A decorated message listener function is called with three arguments every time the
        specified message is received:

        * ``self`` - the current vehicle.
        * ``name`` - the name of the message that was intercepted.
        * ``message`` - the actual message (a `pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_
          `class <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_).

        For example, in the fragment below ``my_method`` will be called for every heartbeat message:

        .. code:: python

            @vehicle.on_message('HEARTBEAT')
            def my_method(self, name, msg):
                pass

        See :ref:`mavlink_messages` for more information.

        :param String name: The name of the message to be intercepted by the decorated listener function (or '*' to get all messages).
        """

        def decorator(fn):
            if isinstance(name, list):
                for n in name:
                    self.add_message_listener(n, fn)
            else:
                self.add_message_listener(name, fn)

        return decorator

    def add_message_listener(self, name, fn):
        """
        Adds a message listener function that will be called every time the specified message is received.

        .. tip::

            We recommend you use :py:func:`on_message` instead of this method as it has a more elegant syntax.
            This method is only preferred if you need to be able to
            :py:func:`remove the listener <remove_message_listener>`.

        The callback function must have three arguments:

        * ``self`` - the current vehicle.
        * ``name`` - the name of the message that was intercepted.
        * ``message`` - the actual message (a `pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_
          `class <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_).

        For example, in the fragment below ``my_method`` will be called for every heartbeat message:

        .. code:: python

            #Callback method for new messages
            def my_method(self, name, msg):
                pass

            vehicle.add_message_listener('HEARTBEAT',my_method)

        See :ref:`mavlink_messages` for more information.

        :param String name: The name of the message to be intercepted by the listener function (or '*' to get all messages).
        :param fn: The listener function that will be called if a message is received.
        """
        name = str(name)
        if name not in self._message_listeners:
            self._message_listeners[name] = []
        if fn not in self._message_listeners[name]:
            self._message_listeners[name].append(fn)

    def remove_message_listener(self, name, fn):
        """
        Removes a message listener (that was previously added using :py:func:`add_message_listener`).

        See :ref:`mavlink_messages` for more information.

        :param String name: The name of the message for which the listener is to be removed (or '*' to remove an 'all messages' observer).
        :param fn: The listener callback function to remove.

        """
        name = str(name)
        if name in self._message_listeners:
            if fn in self._message_listeners[name]:
                self._message_listeners[name].remove(fn)
                if len(self._message_listeners[name]) == 0:
                    del self._message_listeners[name]

    def notify_message_listeners(self, name, msg):
        for fn in self._message_listeners.get(name, []):
            try:
                fn(self, name, msg)
            except Exception:
                self._logger.exception('Exception in message handler for %s' % msg.get_type(), exc_info=True)

        for fn in self._message_listeners.get('*', []):
            try:
                fn(self, name, msg)
            except Exception:
                self._logger.exception('Exception in message handler for %s' % msg.get_type(), exc_info=True)

    def close(self):
        return self._handler.close()

    def flush(self):
        """
        Call ``flush()`` after :py:func:`adding <CommandSequence.add>` or :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``flush()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.

        .. warning::

            This method is deprecated. It has been replaced by
            :py:func:`Vehicle.commands.upload() <Vehicle.commands.upload>`.
        """
        return self.commands.upload()

    #
    # Private sugar methods
    #

    @property
    def _mode_mapping(self):
        return self._master.mode_mapping()

    @property
    def _mode_mapping_bynumber(self):
        return mavutil.mode_mapping_bynumber(self._vehicle_type)

    def _is_mode_available(self, custommode_code, basemode_code=0):
        try:
            if self._autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
                mode = mavutil.interpret_px4_mode(basemode_code, custommode_code)
                return mode in self._mode_mapping
            return custommode_code in self._mode_mapping_bynumber
        except:
            return False

    #
    # Operations to support the standard API.
    #

    @property
    def mode(self):
        """
        This attribute is used to get and set the current flight mode. You
        can specify the value as a :py:class:`VehicleMode`, like this:

        .. code-block:: python

           vehicle.mode = VehicleMode('LOITER')

        Or as a simple string:

        .. code-block:: python

            vehicle.mode = 'LOITER'

        If you are targeting ArduPilot you can also specify the flight mode
        using a numeric value (this will not work with PX4 autopilots):

        .. code-block:: python

            # set mode to LOITER
            vehicle.mode = 5
        """
        if not self._flightmode:
            return None
        return VehicleMode(self._flightmode)

    @mode.setter
    def mode(self, v):
        if isinstance(v, basestring):
            v = VehicleMode(v)

        if self._autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_PX4:
            self._master.set_mode(v.name)
        elif isinstance(v, int):
            self._master.set_mode(v)
        else:
            self._master.set_mode(self._mode_mapping[v.name])

    @property
    def location(self):
        """
        The vehicle location in global, global relative and local frames (:py:class:`Locations`).

        The different frames are accessed through its members:

        * :py:attr:`global_frame <dronekit.Locations.global_frame>` (:py:class:`LocationGlobal`)
        * :py:attr:`global_relative_frame <dronekit.Locations.global_relative_frame>` (:py:class:`LocationGlobalRelative`)
        * :py:attr:`local_frame <dronekit.Locations.local_frame>` (:py:class:`LocationLocal`)

        For example, to print the location in each frame for a ``vehicle``:

        .. code-block:: python

            # Print location information for `vehicle` in all frames (default printer)
            print "Global Location: %s" % vehicle.location.global_frame
            print "Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
            print "Local Location: %s" % vehicle.location.local_frame    #NED

            # Print altitudes in the different frames (see class definitions for other available information)
            print "Altitude (global frame): %s" % vehicle.location.global_frame.alt
            print "Altitude (global relative frame): %s" % vehicle.location.global_relative_frame.alt
            print "Altitude (NED frame): %s" % vehicle.location.local_frame.down

        .. note::

            All the location "values" (e.g. ``global_frame.lat``) are initially
            created with value ``None``. The ``global_frame``, ``global_relative_frame``
            latitude and longitude values are populated shortly after initialisation but
            ``global_frame.alt`` may take a few seconds longer to be updated.
            The ``local_frame`` does not populate until the vehicle is armed.

        The attribute and its members are observable. To watch for changes in all frames using a listener
        created using a decorator (you can also define a listener and explicitly add it).

        .. code-block:: python

            @vehicle.on_attribute('location')
            def listener(self, attr_name, value):
                # `self`: :py:class:`Vehicle` object that has been updated.
                # `attr_name`: name of the observed attribute - 'location'
                # `value` is the updated attribute value (a :py:class:`Locations`). This can be queried for the frame information
                print " Global: %s" % value.global_frame
                print " GlobalRelative: %s" % value.global_relative_frame
                print " Local: %s" % value.local_frame

        To watch for changes in just one attribute (in this case ``global_frame``):

        .. code-block:: python

            @vehicle.on_attribute('location.global_frame')
            def listener(self, attr_name, value):
                # `self`: :py:class:`Locations` object that has been updated.
                # `attr_name`: name of the observed attribute - 'global_frame'
                # `value` is the updated attribute value.
                print " Global: %s" % value

            #Or watch using decorator: ``@vehicle.location.on_attribute('global_frame')``.
        """
        return self._location

    @property
    def wind(self):
        """
        Current wind status (:pu:class: `Wind`)
        """
        if self._wind_direction is None or self._wind_speed is None or self._wind_speed_z is None:
            return None
        return Wind(self._wind_direction, self._wind_speed, self._wind_speed_z)

    @property
    def battery(self):
        """
        Current system batter status (:py:class:`Battery`).
        """
        if self._voltage is None or self._current is None or self._level is None:
            return None
        return Battery(self._voltage, self._current, self._level)

    @property
    def rangefinder(self):
        """
        Rangefinder distance and voltage values (:py:class:`Rangefinder`).
        """
        return Rangefinder(self._rngfnd_distance, self._rngfnd_voltage)

    @property
    def velocity(self):
        """
        Current velocity as a three element list ``[ vx, vy, vz ]`` (in meter/sec).
        """
        return [self._vx, self._vy, self._vz]

    @property
    def version(self):
        """
        The autopilot version and type in a :py:class:`Version` object.

        .. versionadded:: 2.0.3
        """
        return Version(self._raw_version, self._autopilot_type, self._vehicle_type)

    @property
    def capabilities(self):
        """
        The autopilot capabilities in a :py:class:`Capabilities` object.

        .. versionadded:: 2.0.3
        """
        return Capabilities(self._capabilities)

    @property
    def attitude(self):
        """
        Current vehicle attitude - pitch, yaw, roll (:py:class:`Attitude`).
        """
        return Attitude(self._pitch, self._yaw, self._roll)

    @property
    def gps_0(self):
        """
        GPS position information (:py:class:`GPSInfo`).
        """
        return GPSInfo(self._eph, self._epv, self._fix_type, self._satellites_visible)

    @property
    def armed(self):
        """
        This attribute can be used to get and set the ``armed`` state of the vehicle (``boolean``).

        The code below shows how to read the state, and to arm/disarm the vehicle:

        .. code:: python

            # Print the armed state for the vehicle
            print "Armed: %s" % vehicle.armed

            # Disarm the vehicle
            vehicle.armed = False

            # Arm the vehicle
            vehicle.armed = True
        """
        return self._armed

    @armed.setter
    def armed(self, value):
        if bool(value) != self._armed:
            if value:
                self._master.arducopter_arm()
            else:
                self._master.arducopter_disarm()

    @property
    def is_armable(self):
        """
        Returns ``True`` if the vehicle is ready to arm, false otherwise (``Boolean``).

        This attribute wraps a number of pre-arm checks, ensuring that the vehicle has booted,
        has a good GPS fix, and that the EKF pre-arm is complete.
        """
        # check that mode is not INITIALSING
        # check that we have a GPS fix
        # check that EKF pre-arm is complete
        return self.mode != 'INITIALISING' and (self.gps_0.fix_type is not None and self.gps_0.fix_type > 1) and self._ekf_predposhorizabs

    @property
    def system_status(self):
        """
        System status (:py:class:`SystemStatus`).

        The status has a ``state`` property with one of the following values:

        * ``UNINIT``: Uninitialized system, state is unknown.
        * ``BOOT``: System is booting up.
        * ``CALIBRATING``: System is calibrating and not flight-ready.
        * ``STANDBY``: System is grounded and on standby. It can be launched any time.
        * ``ACTIVE``: System is active and might be already airborne. Motors are engaged.
        * ``CRITICAL``: System is in a non-normal flight mode. It can however still navigate.
        * ``EMERGENCY``: System is in a non-normal flight mode. It lost control over parts
          or over the whole airframe. It is in mayday and going down.
        * ``POWEROFF``: System just initialized its power-down sequence, will shut down now.
        """
        return {
            0: SystemStatus('UNINIT'),
            1: SystemStatus('BOOT'),
            2: SystemStatus('CALIBRATING'),
            3: SystemStatus('STANDBY'),
            4: SystemStatus('ACTIVE'),
            5: SystemStatus('CRITICAL'),
            6: SystemStatus('EMERGENCY'),
            7: SystemStatus('POWEROFF'),
        }.get(self._system_status, None)

    @property
    def heading(self):
        """
        Current heading in degrees - 0..360, where North = 0 (``int``).
        """
        return self._heading

    @property
    def groundspeed(self):
        """
        Current groundspeed in metres/second (``double``).

        This attribute is settable. The set value is the default target groundspeed
        when moving the vehicle using :py:func:`simple_goto` (or other position-based
        movement commands).
        """
        return self._groundspeed

    @groundspeed.setter
    def groundspeed(self, speed):
        speed_type = 1  # ground speed
        msg = self.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # command
            0,  # confirmation
            speed_type,  # param 1
            speed,  # speed in metres/second
            -1, 0, 0, 0, 0  # param 3 - 7
        )

        # send command to vehicle
        self.send_mavlink(msg)

    @property
    def airspeed(self):
        """
        Current airspeed in metres/second (``double``).

        This attribute is settable. The set value is the default target airspeed
        when moving the vehicle using :py:func:`simple_goto` (or other position-based
        movement commands).
        """
        return self._airspeed

    @airspeed.setter
    def airspeed(self, speed):
        speed_type = 0  # air speed
        msg = self.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,  # command
            0,  # confirmation
            speed_type,  # param 1
            speed,  # speed in metres/second
            -1, 0, 0, 0, 0  # param 3 - 7
        )

        # send command to vehicle
        self.send_mavlink(msg)

    @property
    def gimbal(self):
        """
        Gimbal object for controlling, viewing and observing gimbal status (:py:class:`Gimbal`).

        .. versionadded:: 2.0.1
        """
        return self._gimbal

    @property
    def mount_status(self):
        """
        .. warning:: This method is deprecated. It has been replaced by :py:attr:`gimbal`.

        Current status of the camera mount (gimbal) as a three element list: ``[ pitch, yaw, roll ]``.

        The values in the list are set to ``None`` if no mount is configured.
        """
        return [self._mount_pitch, self._mount_yaw, self._mount_roll]

    @property
    def ekf_ok(self):
        """
        ``True`` if the EKF status is considered acceptable, ``False`` otherwise (``boolean``).
        """
        # legacy check for dronekit-python for solo
        # use same check that ArduCopter::system.pde::position_ok() is using
        if self.armed:
            return self._ekf_poshorizabs and not self._ekf_constposmode
        else:
            return self._ekf_poshorizabs or self._ekf_predposhorizabs

    @property
    def channels(self):
        """
        The RC channel values from the RC Transmitter (:py:class:`Channels`).

        The attribute can also be used to set and read RC Override (channel override) values
        via :py:attr:`Vehicle.channels.override <dronekit.Channels.overrides>`.

        For more information and examples see :ref:`example_channel_overrides`.

        To read the channels from the RC transmitter:

        .. code:: python

            # Get all channel values from RC transmitter
            print "Channel values from RC Tx:", vehicle.channels

            # Access channels individually
            print "Read channels individually:"
            print " Ch1: %s" % vehicle.channels['1']
            print " Ch2: %s" % vehicle.channels['2']

        """
        return self._channels

    @property
    def home_location(self):
        """
        The current home location (:py:class:`LocationGlobal`).

        To get the attribute you must first download the :py:func:`Vehicle.commands`.
        The attribute has a value of ``None`` until :py:func:`Vehicle.commands` has been downloaded
        **and** the autopilot has set an initial home location (typically where the vehicle first gets GPS lock).

        .. code-block:: python

            #Connect to a vehicle object (for example, on com14)
            vehicle = connect('com14', wait_ready=True)

            # Download the vehicle waypoints (commands). Wait until download is complete.
            cmds = vehicle.commands
            cmds.download()
            cmds.wait_ready()

            # Get the home location
            home = vehicle.home_location

        The ``home_location`` is not observable.

        The attribute can be written (in the same way as any other attribute) after it has successfully
        been populated from the vehicle. The value sent to the vehicle is cached in the attribute
        (and can potentially get out of date if you don't re-download ``Vehicle.commands``):

        .. warning::

            Setting the value will fail silently if the specified location is more than 50km from the EKF origin.


        """
        return copy.copy(self._home_location)

    @home_location.setter
    def home_location(self, pos):
        """
        Sets the home location (``LocationGlobal``).

        The value cannot be set until it has successfully been read from the vehicle. After being
        set the value is cached in the home_location attribute and does not have to be re-read.

        .. note::

            Setting the value will fail silently if the specified location is more than 50km from the EKF origin.
        """

        if not isinstance(pos, LocationGlobal):
            raise ValueError('Expecting home_location to be set to a LocationGlobal.')

        # Set cached home location.
        self._home_location = copy.copy(pos)

        # Send MAVLink update.
        self.send_mavlink(self.message_factory.command_long_encode(
            0, 0,  # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_HOME,  # command
            0,  # confirmation
            0,  # param 1: 1 to use current position, 0 to use the entered values.
            0, 0, 0,  # params 2-4
            pos.lat, pos.lon, pos.alt))

    @property
    def commands(self):
        """
        Gets the editable waypoints/current mission for this vehicle (:py:class:`CommandSequence`).

        This can be used to get, create, and modify a mission.

        :returns: A :py:class:`CommandSequence` containing the waypoints for this vehicle.
        """
        return self._commands

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle (:py:class:`Parameters`).
        """
        return self._parameters

    def wait_for(self, condition, timeout=None, interval=0.1, errmsg=None):
        '''Wait for a condition to be True.

        Wait for condition, a callable, to return True.  If timeout is
        nonzero, raise a TimeoutError(errmsg) if the condition is not
        True after timeout seconds.  Check the condition everal
        interval seconds.
        '''

        t0 = time.time()
        while not condition():
            t1 = time.time()
            if timeout and (t1 - t0) >= timeout:
                raise TimeoutError(errmsg)

            time.sleep(interval)

    def wait_for_armable(self, timeout=None):
        '''Wait for the vehicle to become armable.

        If timeout is nonzero, raise a TimeoutError if the vehicle
        is not armable after timeout seconds.
        '''

        def check_armable():
            return self.is_armable

        self.wait_for(check_armable, timeout=timeout)

    def arm(self, wait=True, timeout=None):
        '''Arm the vehicle.

        If wait is True, wait for arm operation to complete before
        returning.  If timeout is nonzero, raise a TimeouTerror if the
        vehicle has not armed after timeout seconds.
        '''

        self.armed = True

        if wait:
            self.wait_for(lambda: self.armed, timeout=timeout,
                          errmsg='failed to arm vehicle')

    def disarm(self, wait=True, timeout=None):
        '''Disarm the vehicle.

        If wait is True, wait for disarm operation to complete before
        returning.  If timeout is nonzero, raise a TimeouTerror if the
        vehicle has not disarmed after timeout seconds.
        '''
        self.armed = False

        if wait:
            self.wait_for(lambda: not self.armed, timeout=timeout,
                          errmsg='failed to disarm vehicle')

    def wait_for_mode(self, mode, timeout=None):
        '''Set the flight mode.

        If wait is True, wait for the mode to change before returning.
        If timeout is nonzero, raise a TimeoutError if the flight mode
        hasn't changed after timeout seconds.
        '''

        if not isinstance(mode, VehicleMode):
            mode = VehicleMode(mode)

        self.mode = mode

        self.wait_for(lambda: self.mode.name == mode.name,
                      timeout=timeout,
                      errmsg='failed to set flight mode')

    def wait_for_alt(self, alt, epsilon=0.1, rel=True, timeout=None):
        '''Wait for the vehicle to reach the specified altitude.

        Wait for the vehicle to get within epsilon meters of the
        given altitude.  If rel is True (the default), use the
        global_relative_frame. If rel is False, use the global_frame.
        If timeout is nonzero, raise a TimeoutError if the specified
        altitude has not been reached after timeout seconds.
        '''

        def get_alt():
            if rel:
                alt = self.location.global_relative_frame.alt
            else:
                alt = self.location.global_frame.alt

            return alt

        def check_alt():
            cur = get_alt()
            delta = abs(alt - cur)

            return (
                (delta < epsilon) or
                (cur > alt > start) or
                (cur < alt < start)
            )

        start = get_alt()

        self.wait_for(
            check_alt,
            timeout=timeout,
            errmsg='failed to reach specified altitude')

    def wait_simple_takeoff(self, alt=None, epsilon=0.1, timeout=None):
        self.simple_takeoff(alt)

        if alt is not None:
            self.wait_for_alt(alt, epsilon=epsilon, timeout=timeout)

    def simple_takeoff(self, alt=None):
        """
        Take off and fly the vehicle to the specified altitude (in metres) and then wait for another command.

        .. note::

            This function should only be used on Copter vehicles.


        The vehicle must be in GUIDED mode and armed before this is called.

        There is no mechanism for notification when the correct altitude is reached,
        and if another command arrives before that point (e.g. :py:func:`simple_goto`) it will be run instead.

        .. warning::

           Apps should code to ensure that the vehicle will reach a safe altitude before
           other commands are executed. A good example is provided in the guide topic :doc:`guide/taking_off`.

        :param alt: Target height, in metres.
        """
        if alt is not None:
            altitude = float(alt)
            if math.isnan(altitude) or math.isinf(altitude):
                raise ValueError("Altitude was NaN or Infinity. Please provide a real number")
            self._master.mav.command_long_send(0, 0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                               0, 0, 0, 0, 0, 0, 0, altitude)

    def simple_goto(self, location, airspeed=None, groundspeed=None):
        '''
        Go to a specified global location (:py:class:`LocationGlobal` or :py:class:`LocationGlobalRelative`).

        There is no mechanism for notification when the target location is reached, and if another command arrives
        before that point that will be executed immediately.

        You can optionally set the desired airspeed or groundspeed (this is identical to setting
        :py:attr:`airspeed` or :py:attr:`groundspeed`). The vehicle will determine what speed to
        use if the values are not set or if they are both set.

        The method will change the :py:class:`VehicleMode` to ``GUIDED`` if necessary.

        .. code:: python

            # Set mode to guided - this is optional as the simple_goto method will change the mode if needed.
            vehicle.mode = VehicleMode("GUIDED")

            # Set the LocationGlobal to head towards
            a_location = LocationGlobal(-34.364114, 149.166022, 30)
            vehicle.simple_goto(a_location)

        :param location: The target location (:py:class:`LocationGlobal` or :py:class:`LocationGlobalRelative`).
        :param airspeed: Target airspeed in m/s (optional).
        :param groundspeed: Target groundspeed in m/s (optional).
        '''
        if isinstance(location, LocationGlobalRelative):
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
            alt = location.alt
        elif isinstance(location, LocationGlobal):
            # This should be the proper code:
            # frame = mavutil.mavlink.MAV_FRAME_GLOBAL
            # However, APM discards information about the relative frame
            # and treats any alt value as relative. So we compensate here.
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
            if not self.home_location:
                self.commands.download()
                self.commands.wait_ready()
            alt = location.alt - self.home_location.alt
        else:
            raise ValueError('Expecting location to be LocationGlobal or LocationGlobalRelative.')

        self._master.mav.mission_item_send(0, 0, 0, frame,
                                           mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 2, 0, 0,
                                           0, 0, 0, location.lat, location.lon,
                                           alt)

        if airspeed is not None:
            self.airspeed = airspeed
        if groundspeed is not None:
            self.groundspeed = groundspeed

    def send_mavlink(self, message):
        """
        This method is used to send raw MAVLink "custom messages" to the vehicle.

        The function can send arbitrary messages/commands to the connected vehicle at any time and in any vehicle mode.
        It is particularly useful for controlling vehicles outside of missions (for example, in GUIDED mode).

        The :py:func:`message_factory <dronekit.Vehicle.message_factory>` is used to create messages in the appropriate format.

        For more information see the guide topic: :ref:`guided_mode_how_to_send_commands`.

        :param message: A ``MAVLink_message`` instance, created using :py:func:`message_factory <dronekit.Vehicle.message_factory>`.
            There is need to specify the system id, component id or sequence number of messages as the API will set these appropriately.
        """
        self._master.mav.send(message)

    @property
    def message_factory(self):
        """
        Returns an object that can be used to create 'raw' MAVLink messages that are appropriate for this vehicle.
        The message can then be sent using :py:func:`send_mavlink(message) <dronekit.Vehicle.send_mavlink>`.

        .. note::

            Vehicles support a subset of the messages defined in the MAVLink standard. For more information
            about the supported sets see wiki topics:
            `Copter Commands in Guided Mode <http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/>`_
            and `Plane Commands in Guided Mode <http://dev.ardupilot.com/wiki/plane-commands-in-guided-mode/>`_.

        All message types are defined in the central MAVLink github repository.  For example, a Pixhawk understands
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

        Some message types include "addressing information". If present, there is no need to specify the ``target_system``
        id (just set to zero) as DroneKit will automatically update messages with the correct ID for the connected
        vehicle before sending.
        The ``target_component`` should be set to 0 (broadcast) unless the message is to specific component.
        CRC fields and sequence numbers (if defined in the message type) are automatically set by DroneKit and can also
        be ignored/set to zero.

        For more information see the guide topic: :ref:`guided_mode_how_to_send_commands`.
        """
        return self._master.mav

    def initialize(self, rate=4, heartbeat_timeout=30):
        self._handler.start()

        # Start heartbeat polling.
        start = monotonic.monotonic()
        self._heartbeat_error = heartbeat_timeout or 0
        self._heartbeat_started = True
        self._heartbeat_lastreceived = start

        # Poll for first heartbeat.
        # If heartbeat times out, this will interrupt.
        while self._handler._alive:
            time.sleep(.1)
            if self._heartbeat_lastreceived != start:
                break
        if not self._handler._alive:
            raise APIException('Timeout in initializing connection.')

        # Register target_system now.
        self._handler.target_system = self._heartbeat_system

        # Wait until board has booted.
        while True:
            if self._flightmode not in [None, 'INITIALISING', 'MAV']:
                break
            time.sleep(0.1)

        # Initialize data stream.
        if rate is not None:
            self._master.mav.request_data_stream_send(0, 0, mavutil.mavlink.MAV_DATA_STREAM_ALL,
                                                      rate, 1)

        self.add_message_listener('HEARTBEAT', self.send_capabilities_request)

        # Ensure initial parameter download has started.
        while True:
            # This fn actually rate limits itself to every 2s.
            # Just retry with persistence to get our first param stream.
            self._master.param_fetch_all()
            time.sleep(0.1)
            if self._params_count > -1:
                break

    def send_capabilties_request(self, vehicle, name, m):
        '''An alias for send_capabilities_request.

        The word "capabilities" was misspelled in previous versions of this code. This is simply
        an alias to send_capabilities_request using the legacy name.
        '''
        return self.send_capabilities_request(vehicle, name, m)

    def send_capabilities_request(self, vehicle, name, m):
        '''Request an AUTOPILOT_VERSION packet'''
        capability_msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES, 0, 1, 0, 0, 0, 0, 0, 0)
        vehicle.send_mavlink(capability_msg)

    def play_tune(self, tune):
        '''Play a tune on the vehicle'''
        msg = self.message_factory.play_tune_encode(0, 0, tune)
        self.send_mavlink(msg)

    def wait_ready(self, *types, **kwargs):
        """
        Waits for specified attributes to be populated from the vehicle (values are initially ``None``).

        This is typically called "behind the scenes" to ensure that :py:func:`connect` does not return until
        attributes have populated (via the ``wait_ready`` parameter). You can also use it after connecting to
        wait on a specific value(s).

        There are two ways to call the method:

        .. code-block:: python

            #Wait on default attributes to populate
            vehicle.wait_ready(True)

            #Wait on specified attributes (or array of attributes) to populate
            vehicle.wait_ready('mode','airspeed')

        Using the ``wait_ready(True)`` waits on :py:attr:`parameters`, :py:attr:`gps_0`,
        :py:attr:`armed`, :py:attr:`mode`, and :py:attr:`attitude`. In practice this usually
        means that all supported attributes will be populated.

        By default, the method will timeout after 30 seconds and raise an exception if the
        attributes were not populated.

        :param types: ``True`` to wait on the default set of attributes, or a
            comma-separated list of the specific attributes to wait on.
        :param int timeout: Timeout in seconds after which the method will raise an exception
            (the default) or return ``False``. The default timeout is 30 seconds.
        :param Boolean raise_exception: If ``True`` the method will raise an exception on timeout,
            otherwise the method will return ``False``. The default is ``True`` (raise exception).
        """
        timeout = kwargs.get('timeout', 30)
        raise_exception = kwargs.get('raise_exception', True)

        # Vehicle defaults for wait_ready(True) or wait_ready()
        if list(types) == [True] or list(types) == []:
            types = self._default_ready_attrs

        if not all(isinstance(item, basestring) for item in types):
            raise ValueError('wait_ready expects one or more string arguments.')

        # Wait for these attributes to have been set.
        await_attributes = set(types)
        start = monotonic.monotonic()
        still_waiting_last_message_sent = start
        still_waiting_callback = kwargs.get('still_waiting_callback')
        still_waiting_message_interval = kwargs.get('still_waiting_interval', 1)

        while not await_attributes.issubset(self._ready_attrs):
            time.sleep(0.1)
            now = monotonic.monotonic()
            if now - start > timeout:
                if raise_exception:
                    raise TimeoutError('wait_ready experienced a timeout after %s seconds.' %
                                       timeout)
                else:
                    return False
            if (still_waiting_callback and
                    now - still_waiting_last_message_sent > still_waiting_message_interval):
                still_waiting_last_message_sent = now
                if still_waiting_callback:
                    still_waiting_callback(await_attributes - self._ready_attrs)

        return True

    def reboot(self):
        """Requests an autopilot reboot by sending a ``MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN`` command."""

        reboot_msg = self.message_factory.command_long_encode(
            0, 0,  # target_system, target_component
            mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,  # command
            0,  # confirmation
            1,  # param 1, autopilot (reboot)
            0,  # param 2, onboard computer (do nothing)
            0,  # param 3, camera (do nothing)
            0,  # param 4, mount (do nothing)
            0, 0, 0)  # param 5 ~ 7 not used

        self.send_mavlink(reboot_msg)

    def send_calibrate_gyro(self):
        """Request gyroscope calibration."""

        calibration_command = self.message_factory.command_long_encode(
            self._handler.target_system, 0,  # target_system, target_component
            mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # command
            0,  # confirmation
            1,  # param 1, 1: gyro calibration, 3: gyro temperature calibration
            0,  # param 2, 1: magnetometer calibration
            0,  # param 3, 1: ground pressure calibration
            0,  # param 4, 1: radio RC calibration, 2: RC trim calibration
            0,  # param 5, 1: accelerometer calibration, 2: board level calibration, 3: accelerometer temperature calibration, 4: simple accelerometer calibration
            0,  # param 6, 2: airspeed calibration
            0,  # param 7, 1: ESC calibration, 3: barometer temperature calibration
        )
        self.send_mavlink(calibration_command)

    def send_calibrate_magnetometer(self):
        """Request magnetometer calibration."""

        # ArduPilot requires the MAV_CMD_DO_START_MAG_CAL command, only present in the ardupilotmega.xml definition
        if self._autopilot_type == mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA:
            calibration_command = self.message_factory.command_long_encode(
                self._handler.target_system, 0,  # target_system, target_component
                mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,  # command
                0,  # confirmation
                0,  # param 1, uint8_t bitmask of magnetometers (0 means all).
                1,  # param 2, Automatically retry on failure (0=no retry, 1=retry).
                1,  # param 3, Save without user input (0=require input, 1=autosave).
                0,  # param 4, Delay (seconds).
                0,  # param 5, Autoreboot (0=user reboot, 1=autoreboot).
                0,  # param 6, Empty.
                0,  # param 7, Empty.
            )
        else:
            calibration_command = self.message_factory.command_long_encode(
                self._handler.target_system, 0,  # target_system, target_component
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # command
                0,  # confirmation
                0,  # param 1, 1: gyro calibration, 3: gyro temperature calibration
                1,  # param 2, 1: magnetometer calibration
                0,  # param 3, 1: ground pressure calibration
                0,  # param 4, 1: radio RC calibration, 2: RC trim calibration
                0,  # param 5, 1: accelerometer calibration, 2: board level calibration, 3: accelerometer temperature calibration, 4: simple accelerometer calibration
                0,  # param 6, 2: airspeed calibration
                0,  # param 7, 1: ESC calibration, 3: barometer temperature calibration
            )

        self.send_mavlink(calibration_command)

    def send_calibrate_accelerometer(self, simple=False):
        """Request accelerometer calibration.

        :param simple: if True, perform simple accelerometer calibration
        """

        calibration_command = self.message_factory.command_long_encode(
            self._handler.target_system, 0,  # target_system, target_component
            mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # command
            0,  # confirmation
            0,  # param 1, 1: gyro calibration, 3: gyro temperature calibration
            0,  # param 2, 1: magnetometer calibration
            0,  # param 3, 1: ground pressure calibration
            0,  # param 4, 1: radio RC calibration, 2: RC trim calibration
            4 if simple else 1,  # param 5, 1: accelerometer calibration, 2: board level calibration, 3: accelerometer temperature calibration, 4: simple accelerometer calibration
            0,  # param 6, 2: airspeed calibration
            0,  # param 7, 1: ESC calibration, 3: barometer temperature calibration
        )
        self.send_mavlink(calibration_command)

    def send_calibrate_vehicle_level(self):
        """Request vehicle level (accelerometer trim) calibration."""

        calibration_command = self.message_factory.command_long_encode(
            self._handler.target_system, 0,  # target_system, target_component
            mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # command
            0,  # confirmation
            0,  # param 1, 1: gyro calibration, 3: gyro temperature calibration
            0,  # param 2, 1: magnetometer calibration
            0,  # param 3, 1: ground pressure calibration
            0,  # param 4, 1: radio RC calibration, 2: RC trim calibration
            2,  # param 5, 1: accelerometer calibration, 2: board level calibration, 3: accelerometer temperature calibration, 4: simple accelerometer calibration
            0,  # param 6, 2: airspeed calibration
            0,  # param 7, 1: ESC calibration, 3: barometer temperature calibration
        )
        self.send_mavlink(calibration_command)

    def send_calibrate_barometer(self):
        """Request barometer calibration."""

        calibration_command = self.message_factory.command_long_encode(
            self._handler.target_system, 0,  # target_system, target_component
            mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,  # command
            0,  # confirmation
            0,  # param 1, 1: gyro calibration, 3: gyro temperature calibration
            0,  # param 2, 1: magnetometer calibration
            1,  # param 3, 1: ground pressure calibration
            0,  # param 4, 1: radio RC calibration, 2: RC trim calibration
            0,  # param 5, 1: accelerometer calibration, 2: board level calibration, 3: accelerometer temperature calibration, 4: simple accelerometer calibration
            0,  # param 6, 2: airspeed calibration
            0,  # param 7, 1: ESC calibration, 3: barometer temperature calibration
        )
        self.send_mavlink(calibration_command)


class Gimbal(object):
    """
    Gimbal status and control.

    An object of this type is returned by :py:attr:`Vehicle.gimbal`. The
    gimbal orientation can be obtained from its :py:attr:`roll`, :py:attr:`pitch` and
    :py:attr:`yaw` attributes.

    The gimbal orientation can be set explicitly using :py:func:`rotate`
    or you can set the gimbal (and vehicle) to track a specific "region of interest" using
    :py:func:`target_location`.

    .. note::

        * The orientation attributes are created with values of ``None``. If a gimbal is present,
          the attributes are populated shortly after initialisation by messages from the autopilot.
        * The attribute values reflect the last gimbal setting-values rather than actual measured values.
          This means that the values won't change if you manually move the gimbal, and that the value
          will change when you set it, even if the specified orientation is not supported.
        * A gimbal may not support all axes of rotation. For example, the Solo gimbal will set pitch
          values from 0 to -90 (straight ahead to straight down), it will rotate the vehicle to follow specified
          yaw values, and will ignore roll commands (not supported).
    """

    def __init__(self, vehicle):
        super(Gimbal, self).__init__()

        self._pitch = None
        self._roll = None
        self._yaw = None
        self._vehicle = vehicle

        @vehicle.on_message('MOUNT_STATUS')
        def listener(vehicle, name, m):
            self._pitch = m.pointing_a / 100.0
            self._roll = m.pointing_b / 100.0
            self._yaw = m.pointing_c / 100.0
            vehicle.notify_attribute_listeners('gimbal', vehicle.gimbal)

        @vehicle.on_message('MOUNT_ORIENTATION')
        def listener(vehicle, name, m):
            self._pitch = m.pitch
            self._roll = m.roll
            self._yaw = m.yaw
            vehicle.notify_attribute_listeners('gimbal', vehicle.gimbal)

    @property
    def pitch(self):
        """
        Gimbal pitch in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
        A value of 0 represents a camera pointed straight ahead relative to the front of the vehicle,
        while -90 points the camera straight down.

        .. note::

            This is the last pitch value sent to the gimbal (not the actual/measured pitch).
        """
        return self._pitch

    @property
    def roll(self):
        """
        Gimbal roll in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).

        .. note::

            This is the last roll value sent to the gimbal (not the actual/measured roll).
        """
        return self._roll

    @property
    def yaw(self):
        """
        Gimbal yaw in degrees relative to *global frame* (0 is North, 90 is West, 180 is South etc).

        .. note::

            This is the last yaw value sent to the gimbal (not the actual/measured yaw).
        """
        return self._yaw

    def rotate(self, pitch, roll, yaw):
        """
        Rotate the gimbal to a specific vector.

        .. code-block:: python

            #Point the gimbal straight down
            vehicle.gimbal.rotate(-90, 0, 0)

        :param pitch: Gimbal pitch in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
            A value of 0 represents a camera pointed straight ahead relative to the front of the vehicle,
            while -90 points the camera straight down.
        :param roll: Gimbal roll in degrees relative to the vehicle (see diagram for :ref:`attitude <figure_attitude>`).
        :param yaw: Gimbal yaw in degrees relative to *global frame* (0 is North, 90 is West, 180 is South etc.)
        """
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING,  #mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)
        msg = self._vehicle.message_factory.mount_control_encode(
            0, 1,    # target system, target component
            pitch * 100,  # pitch is in centidegrees
            roll * 100,  # roll
            yaw * 100,  # yaw is in centidegrees
            0  # save position
        )
        self._vehicle.send_mavlink(msg)

    def target_location(self, roi):
        """
        Point the gimbal at a specific region of interest (ROI).

        .. code-block:: python

            #Set the camera to track the current home location.
            vehicle.gimbal.target_location(vehicle.home_location)

        The target position must be defined in a :py:class:`LocationGlobalRelative` or :py:class:`LocationGlobal`.

        This function can be called in AUTO or GUIDED mode.

        In order to clear an ROI you can send a location with all zeros (e.g. ``LocationGlobalRelative(0,0,0)``).

        :param roi: Target location in global relative frame.
        """
        # set gimbal to targeting mode
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_GPS_POINT,  # mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)

        # Get altitude relative to home irrespective of Location object passed in.
        if isinstance(roi, LocationGlobalRelative):
            alt = roi.alt
        elif isinstance(roi, LocationGlobal):
            if not self.home_location:
                self.commands.download()
                self.commands.wait_ready()
            alt = roi.alt - self.home_location.alt
        else:
            raise ValueError('Expecting location to be LocationGlobal or LocationGlobalRelative.')

        # set the ROI
        msg = self._vehicle.message_factory.command_long_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_ROI,  # command
            0,  # confirmation
            0, 0, 0, 0,  # params 1-4
            roi.lat,
            roi.lon,
            alt
        )
        self._vehicle.send_mavlink(msg)

    def release(self):
        """
        Release control of the gimbal to the user (RC Control).

        This should be called once you've finished controlling the mount with either :py:func:`rotate`
        or :py:func:`target_location`. Control will automatically be released if you change vehicle mode.
        """
        msg = self._vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_RC_TARGETING,  # mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
        )
        self._vehicle.send_mavlink(msg)

    def __str__(self):
        return "Gimbal: pitch={0}, roll={1}, yaw={2}".format(self.pitch, self.roll, self.yaw)


class Parameters(MutableMapping, HasObservers):
    """
    This object is used to get and set the values of named parameters for a vehicle. See the following links for information about
    the supported parameters for each platform: `Copter Parameters <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/>`_,
    `Plane Parameters <http://plane.ardupilot.com/wiki/arduplane-parameters/>`_, `Rover Parameters <http://rover.ardupilot.com/wiki/apmrover2-parameters/>`_.

    The code fragment below shows how to get and set the value of a parameter.

    .. code:: python

        # Print the value of the THR_MIN parameter.
        print "Param: %s" % vehicle.parameters['THR_MIN']

        # Change the parameter value to something different.
        vehicle.parameters['THR_MIN']=100

    It is also possible to observe parameters and to iterate the :py:attr:`Vehicle.parameters`.

    For more information see :ref:`the guide <vehicle_state_parameters>`.
    """

    def __init__(self, vehicle):
        super(Parameters, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._vehicle = vehicle

    def __getitem__(self, name):
        name = name.upper()
        self.wait_ready()
        return self._vehicle._params_map[name]

    def __setitem__(self, name, value):
        name = name.upper()
        self.wait_ready()
        self.set(name, value)

    def __delitem__(self, name):
        raise APIException('Cannot delete value from parameters list.')

    def __len__(self):
        return len(self._vehicle._params_map)

    def __iter__(self):
        return self._vehicle._params_map.__iter__()

    def get(self, name, wait_ready=True):
        name = name.upper()
        if wait_ready:
            self.wait_ready()
        return self._vehicle._params_map.get(name, None)

    def set(self, name, value, retries=3, wait_ready=False):
        if wait_ready:
            self.wait_ready()

        # TODO dumbly reimplement this using timeout loops
        # because we should actually be awaiting an ACK of PARAM_VALUE
        # changed, but we don't have a proper ack structure, we'll
        # instead just wait until the value itself was changed

        name = name.upper()
        # convert to single precision floating point number (the type used by low level mavlink messages)
        value = float(struct.unpack('f', struct.pack('f', value))[0])
        remaining = retries
        while True:
            self._vehicle._master.param_set_send(name, value)
            tstart = monotonic.monotonic()
            if remaining == 0:
                break
            remaining -= 1
            while monotonic.monotonic() - tstart < 1:
                if name in self._vehicle._params_map and self._vehicle._params_map[name] == value:
                    return True
                time.sleep(0.1)

        if retries > 0:
            self._logger.error("timeout setting parameter %s to %f" % (name, value))
        return False

    def wait_ready(self, **kwargs):
        """
        Block the calling thread until parameters have been downloaded
        """
        self._vehicle.wait_ready('parameters', **kwargs)

    def add_attribute_listener(self, attr_name, *args, **kwargs):
        """
        Add a listener callback on a particular parameter.

        The callback can be removed using :py:func:`remove_attribute_listener`.

        .. note::

            The :py:func:`on_attribute` decorator performs the same operation as this method, but with
            a more elegant syntax. Use ``add_attribute_listener`` only if you will need to remove
            the observer.

        The callback function is invoked only when the parameter changes.

        The callback arguments are:

        * ``self`` - the associated :py:class:`Parameters`.
        * ``attr_name`` - the parameter name. This can be used to infer which parameter has triggered
          if the same callback is used for watching multiple parameters.
        * ``msg`` - the new parameter value (so you don't need to re-query the vehicle object).

        The example below shows how to get callbacks for the ``THR_MIN`` parameter:

        .. code:: python

            #Callback function for the THR_MIN parameter
            def thr_min_callback(self, attr_name, value):
                print " PARAMETER CALLBACK: %s changed to: %s" % (attr_name, value)

            #Add observer for the vehicle's THR_MIN parameter
            vehicle.parameters.add_attribute_listener('THR_MIN', thr_min_callback)

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param String attr_name: The name of the parameter to watch (or '*' to watch all parameters).
        :param args: The callback to invoke when a change in the parameter is detected.

        """
        attr_name = attr_name.upper()
        return super(Parameters, self).add_attribute_listener(attr_name, *args, **kwargs)

    def remove_attribute_listener(self, attr_name, *args, **kwargs):
        """
        Remove a paremeter listener that was previously added using :py:func:`add_attribute_listener`.

        For example to remove the ``thr_min_callback()`` callback function:

        .. code:: python

            vehicle.parameters.remove_attribute_listener('thr_min', thr_min_callback)

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param String attr_name: The parameter name that is to have an observer removed (or '*' to remove an 'all attribute' observer).
        :param args: The callback function to remove.

        """
        attr_name = attr_name.upper()
        return super(Parameters, self).remove_attribute_listener(attr_name, *args, **kwargs)

    def notify_attribute_listeners(self, attr_name, *args, **kwargs):
        attr_name = attr_name.upper()
        return super(Parameters, self).notify_attribute_listeners(attr_name, *args, **kwargs)

    def on_attribute(self, attr_name, *args, **kwargs):
        """
        Decorator for parameter listeners.

        .. note::

            There is no way to remove a listener added with this decorator. Use
            :py:func:`add_attribute_listener` if you need to be able to remove
            the :py:func:`listener <remove_attribute_listener>`.

        The callback function is invoked only when the parameter changes.

        The callback arguments are:

        * ``self`` - the associated :py:class:`Parameters`.
        * ``attr_name`` - the parameter name. This can be used to infer which parameter has triggered
          if the same callback is used for watching multiple parameters.
        * ``msg`` - the new parameter value (so you don't need to re-query the vehicle object).

        The code fragment below shows how to get callbacks for the ``THR_MIN`` parameter:

        .. code:: python

            @vehicle.parameters.on_attribute('THR_MIN')
            def decorated_thr_min_callback(self, attr_name, value):
                print " PARAMETER CALLBACK: %s changed to: %s" % (attr_name, value)

        See :ref:`vehicle_state_observing_parameters` for more information.

        :param String attr_name: The name of the parameter to watch (or '*' to watch all parameters).
        :param args: The callback to invoke when a change in the parameter is detected.

        """
        attr_name = attr_name.upper()
        return super(Parameters, self).on_attribute(attr_name, *args, **kwargs)


class Command(mavutil.mavlink.MAVLink_mission_item_message):
    """
    A waypoint object.

    This object encodes a single mission item command. The set of commands that are supported
    by ArduPilot in Copter, Plane and Rover (along with their parameters) are listed in the wiki article
    `MAVLink Mission Command Messages (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.

    For example, to create a `NAV_WAYPOINT <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_nav_waypoint>`_ command:

    .. code:: python

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,-34.364114, 149.166022, 30)

    :param target_system: This can be set to any value
        (DroneKit changes the value to the MAVLink ID of the connected vehicle before the command is sent).
    :param target_component: The component id if the message is intended for a particular component within the target system
        (for example, the camera). Set to zero (broadcast) in most cases.
    :param seq: The sequence number within the mission (the autopilot will reject messages sent out of sequence).
        This should be set to zero as the API will automatically set the correct value when uploading a mission.
    :param frame: The frame of reference used for the location parameters (x, y, z). In most cases this will be
        ``mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT``, which uses the WGS84 global coordinate system for latitude and longitude, but sets altitude
        as relative to the home position in metres (home altitude = 0). For more information `see the wiki here
        <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#frames_of_reference>`_.
    :param command: The specific mission command (e.g. ``mavutil.mavlink.MAV_CMD_NAV_WAYPOINT``). The supported commands (and command parameters
        are listed `on the wiki <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.
    :param current: Set to zero (not supported).
    :param autocontinue: Set to zero (not supported).
    :param param1: Command specific parameter (depends on specific `Mission Command (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_).
    :param param2: Command specific parameter.
    :param param3: Command specific parameter.
    :param param4: Command specific parameter.
    :param x: (param5) Command specific parameter used for latitude (if relevant to command).
    :param y: (param6) Command specific parameter used for longitude (if relevant to command).
    :param z: (param7) Command specific parameter used for altitude (if relevant). The reference frame for altitude depends on the ``frame``.

    """
    pass


class CommandSequence(object):
    """
    A sequence of vehicle waypoints (a "mission").

    Operations include 'array style' indexed access to the various contained waypoints.

    The current commands/mission for a vehicle are accessed using the :py:attr:`Vehicle.commands` attribute.
    Waypoints are not downloaded from vehicle until :py:func:`download()` is called.  The download is asynchronous;
    use :py:func:`wait_ready()` to block your thread until the download is complete.
    The code to download the commands from a vehicle is shown below:

    .. code-block:: python
        :emphasize-lines: 5-10

        #Connect to a vehicle object (for example, on com14)
        vehicle = connect('com14', wait_ready=True)

        # Download the vehicle waypoints (commands). Wait until download is complete.
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()

    The set of commands can be changed and uploaded to the client. The changes are not guaranteed to be complete until
    :py:func:`upload() <Vehicle.commands.upload>` is called.

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
        cmds.upload()

    """

    def __init__(self, vehicle):
        self._vehicle = vehicle

    def download(self):
        '''
        Download all waypoints from the vehicle.
        The download is asynchronous. Use :py:func:`wait_ready()` to block your thread until the download is complete.
        '''
        self.wait_ready()
        self._vehicle._ready_attrs.remove('commands')
        self._vehicle._wp_loaded = False
        self._vehicle._master.waypoint_request_list_send()
        # BIG FIXME - wait for full wpt download before allowing any of the accessors to work

    def wait_ready(self, **kwargs):
        """
        Block the calling thread until waypoints have been downloaded.

        This can be called after :py:func:`download()` to block the thread until the asynchronous download is complete.
        """
        return self._vehicle.wait_ready('commands', **kwargs)

    def clear(self):
        '''
        Clear the command list.

        This command will be sent to the vehicle only after you call :py:func:`upload() <Vehicle.commands.upload>`.
        '''

        # Add home point again.
        self.wait_ready()
        home = None
        try:
            home = self._vehicle._wploader.wp(0)
        except:
            pass
        self._vehicle._wploader.clear()
        if home:
            self._vehicle._wploader.add(home, comment='Added by DroneKit')
        self._vehicle._wpts_dirty = True

    def add(self, cmd):
        '''
        Add a new command (waypoint) at the end of the command list.

        .. note::

            Commands are sent to the vehicle only after you call ::py:func:`upload() <Vehicle.commands.upload>`.

        :param Command cmd: The command to be added.
        '''
        self.wait_ready()
        self._vehicle._handler.fix_targets(cmd)
        self._vehicle._wploader.add(cmd, comment='Added by DroneKit')
        self._vehicle._wpts_dirty = True

    def upload(self, timeout=None):
        """
        Call ``upload()`` after :py:func:`adding <CommandSequence.add>` or :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``upload()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.

        :param int timeout: The timeout for uploading the mission. No timeout if not provided or set to None.
        """
        if self._vehicle._wpts_dirty:
            self._vehicle._master.waypoint_clear_all_send()
            start_time = time.time()
            if self._vehicle._wploader.count() > 0:
                self._vehicle._wp_uploaded = [False] * self._vehicle._wploader.count()
                self._vehicle._master.waypoint_count_send(self._vehicle._wploader.count())
                while False in self._vehicle._wp_uploaded:
                    if timeout and time.time() - start_time > timeout:
                        raise TimeoutError
                    time.sleep(0.1)
                self._vehicle._wp_uploaded = None
            self._vehicle._wpts_dirty = False

    @property
    def count(self):
        '''
        Return number of waypoints.

        :return: The number of waypoints in the sequence.
        '''
        return max(self._vehicle._wploader.count() - 1, 0)

    @property
    def next(self):
        """
        Get the currently active waypoint number.
        """
        return self._vehicle._current_waypoint

    @next.setter
    def next(self, index):
        """
        Set a new ``next`` waypoint for the vehicle.
        """
        self._vehicle._master.waypoint_set_current_send(index)

    def __len__(self):
        '''
        Return number of waypoints.

        :return: The number of waypoints in the sequence.
        '''
        return max(self._vehicle._wploader.count() - 1, 0)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[ii] for ii in range(*index.indices(len(self)))]
        elif isinstance(index, int):
            item = self._vehicle._wploader.wp(index + 1)
            if not item:
                raise IndexError('Index %s out of range.' % index)
            return item
        else:
            raise TypeError('Invalid argument type.')

    def __setitem__(self, index, value):
        self._vehicle._wploader.set(value, index + 1)
        self._vehicle._wpts_dirty = True


def default_still_waiting_callback(atts):
    logging.getLogger(__name__).debug("Still waiting for data from vehicle: %s" % ','.join(atts))


def connect(ip,
            _initialize=True,
            wait_ready=None,
            timeout=30,
            still_waiting_callback=default_still_waiting_callback,
            still_waiting_interval=1,
            status_printer=None,
            vehicle_class=None,
            rate=4,
            baud=115200,
            heartbeat_timeout=30,
            source_system=255,
            source_component=0,
            use_native=False):
    """
    Returns a :py:class:`Vehicle` object connected to the address specified by string parameter ``ip``.
    Connection string parameters (``ip``) for different targets are listed in the :ref:`getting started guide <get_started_connecting>`.

    The method is usually called with ``wait_ready=True`` to ensure that vehicle parameters and (most) attributes are
    available when ``connect()`` returns.

    .. code:: python

        from dronekit import connect

        # Connect to the Vehicle using "connection string" (in this case an address on network)
        vehicle = connect('127.0.0.1:14550', wait_ready=True)

    :param String ip: :ref:`Connection string <get_started_connecting>` for target address - e.g. 127.0.0.1:14550.

    :param Bool/Array wait_ready: If ``True`` wait until all default attributes have downloaded before
        the method returns (default is ``None``).
        The default attributes to wait on are: :py:attr:`parameters`, :py:attr:`gps_0`,
        :py:attr:`armed`, :py:attr:`mode`, and :py:attr:`attitude`.

        You can also specify a named set of parameters to wait on (e.g. ``wait_ready=['system_status','mode']``).

        For more information see :py:func:`Vehicle.wait_ready <Vehicle.wait_ready>`.

    :param status_printer: (deprecated) method of signature ``def status_printer(txt)`` that prints
        STATUS_TEXT messages from the Vehicle and other diagnostic information.
        By default the status information is handled by the ``autopilot`` logger.
    :param Vehicle vehicle_class: The class that will be instantiated by the ``connect()`` method.
        This can be any sub-class of ``Vehicle`` (and defaults to ``Vehicle``).
    :param int rate: Data stream refresh rate. The default is 4Hz (4 updates per second).
    :param int baud: The baud rate for the connection. The default is 115200.
    :param int heartbeat_timeout: Connection timeout value in seconds (default is 30s).
        If a heartbeat is not detected within this time an exception will be raised.
    :param int source_system: The MAVLink ID of the :py:class:`Vehicle` object returned by this method (by default 255).
    :param int source_component: The MAVLink Component ID fo the :py:class:`Vehicle` object returned by this method (by default 0).
    :param bool use_native: Use precompiled MAVLink parser.

        .. note::

            The returned :py:class:`Vehicle` object acts as a ground control station from the
            perspective of the connected "real" vehicle. It will process/receive messages from the real vehicle
            if they are addressed to this ``source_system`` id. Messages sent to the real vehicle are
            automatically updated to use the vehicle's ``target_system`` id.

            It is *good practice* to assign a unique id for every system on the MAVLink network.
            It is possible to configure the autopilot to only respond to guided-mode commands from a specified GCS ID.

            The ``status_printer`` argument is deprecated. To redirect the logging from the library and from the
            autopilot, configure the ``dronekit`` and ``autopilot`` loggers using the Python ``logging`` module.


    :returns: A connected vehicle of the type defined in ``vehicle_class`` (a superclass of :py:class:`Vehicle`).
    """

    from dronekit.mavlink import MAVConnection

    if not vehicle_class:
        vehicle_class = Vehicle

    handler = MAVConnection(ip, baud=baud, source_system=source_system, source_component=source_component, use_native=use_native)
    vehicle = vehicle_class(handler)

    if status_printer:
        vehicle._autopilot_logger.addHandler(ErrprinterHandler(status_printer))

    if _initialize:
        vehicle.initialize(rate=rate, heartbeat_timeout=heartbeat_timeout)

    if wait_ready:
        if wait_ready is True:
            vehicle.wait_ready(still_waiting_interval=still_waiting_interval,
                               still_waiting_callback=still_waiting_callback,
                               timeout=timeout)
        else:
            vehicle.wait_ready(*wait_ready)

    return vehicle
