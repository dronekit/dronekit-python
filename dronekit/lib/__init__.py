"""
This is the API Reference for the DroneKit-Python API.

The main API is the :py:class:`Vehicle <dronekit.lib.Vehicle>` class.
The code snippet below shows how to use :py:func:`connect` to obtain an instance a connected vehicle:

.. code:: python

    from dronekit import connect

    # Connect to the Vehicle using "connection string" (in this case an address on network)
    vehicle = connect('127.0.0.1:14550', wait_ready=True)

:py:class:`Vehicle <dronekit.lib.Vehicle>` provides access to vehicle *state* through python attributes
(e.g. :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>`)
and to settings/parameters though the :py:attr:`Vehicle.parameters <dronekit.lib.Vehicle.parameters>` attribute.
Asynchronous notification on vehicle attribute changes is available by registering observers.

:py:class:`Vehicle <dronekit.lib.Vehicle>` provides two main ways to control vehicle movement and other operations:

* Direct control of movement outside of missions is also supported. To set a target position you can use
  :py:func:`CommandSequence.goto <dronekit.lib.CommandSequence.goto>`.
  Control over speed, direction, altitude, camera trigger and any other aspect of the vehicle is supported using custom MAVLink messages
  (:py:func:`Vehicle.send_mavlink <dronekit.lib.Vehicle.send_mavlink>`, :py:func:`Vehicle.message_factory <dronekit.lib.Vehicle.message_factory>`).
* Missions are downloaded and uploaded through the :py:attr:`Vehicle.commands <dronekit.lib.Vehicle.commands>` attribute
  (see :py:class:`CommandSequence <dronekit.lib.CommandSequence>` for more information).

A number of other useful classes and methods are listed below.

----

.. todo:: Update this when have confirmed how to register for parameter notifications.

.. py:function:: connect(ip, wait_ready=False, status_printer=errprinter, vehicle_class=Vehicle, rate=4, baud=115200)

    Returns a :py:class:`Vehicle` object connected to the address specified by string parameter ``ip``. 
    Connection string parameters for different targets are listed in the :ref:`getting started guide <get_started_connecting>`.

    :param String ip: Connection string for target address - e.g. 127.0.0.1:14550.
    :param Bool wait_ready: Wait until all :py:func:`Vehicle.parameters` have downloaded before the method returns (default is false)
    :param status_printer: NA    
    :param Vehicle vehicle_class: NA     
    :param int rate: NA
    :param int baud: The baud rate for the connection. The default is 115200.
    
    :returns: A connected :py:class:`Vehicle` object.

----

    .. todo:: 
    
        Confirm what status_printer, vehicle_class and rate "mean" (https://github.com/dronekit/dronekit-python/issues/395#issuecomment-153527657)
        Can we hide in API. Can we get method defined in this file or connect method file exported
        
"""

# DroneAPI module

import threading, time, math, copy
import CloudClient
from pymavlink.dialects.v10 import ardupilotmega
from pymavlink import mavutil, mavwp
from dronekit.util import errprinter

local_path = ''

class APIException(Exception):
    """
    Base class for DroneKit related exceptions.

    :param String msg: Message string describing the exception
    """

    def __init__(self, msg):
        self.msg = msg

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

class LocationGlobal(object):
    """
    A global location object.

    The latitude and longitude are relative to the `WGS84 coordinate system <http://en.wikipedia.org/wiki/World_Geodetic_System>`_.
    The altitude is relative to either the *home position* or "mean sea-level", depending on the value of the ``is_relative``.

    For example, a global location object might be defined as:

    .. code:: python

       LocationGlobal(-34.364114, 149.166022, 30, is_relative=True)

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

        # This is for backward compatibility.
        self.local_frame = None
        self.global_fame = None

    def __str__(self):
        return "LocationGlobal:lat=%s,lon=%s,alt=%s,is_relative=%s" % (self.lat, self.lon, self.alt, self.is_relative)

# Back-compatibility for earlier clients.
Location = LocationGlobal

class LocationLocal(object):
    """
    A local location object.

    The north, east and down are relative to the EKF origin.  This is most likely the location where the vehicle was turned on.  

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

class GPSInfo(object):
    """
    Standard information about GPS.

    If there is no GPS lock the parameters are set to ``None``.

    :param IntType eph: GPS horizontal dilution of position (HDOP).
    :param IntType epv: GPS horizontal dilution of position (VDOP).
    :param IntType fix_type: 0-1: no fix, 2: 2D fix, 3: 3D fix
    :param IntType satellites_visible: Number of satellites visible.

    .. todo:: FIXME: GPSInfo class - possibly normalize eph/epv?  report fix type as string?
    """
    def __init__(self, eph, epv, fix_type, satellites_visible):
        self.eph = eph
        self.epv = epv
        self.fix_type = fix_type
        self.satellites_visible = satellites_visible

    def __str__(self):
        return "GPSInfo:fix=%s,num_sat=%s" % (self.fix_type, self.satellites_visible)

class Battery(object):
    """
    System battery information.

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
        return "Battery:voltage={},current={},level={}".format(self.voltage, self.current, self.level)

class Rangefinder(object):
    """
    Rangefinder readings.

    :param distance: Distance (metres). ``None`` if the vehicle doesn't have a rangefinder.
    :param voltage: Voltage (volts). ``None`` if the vehicle doesn't have a rangefinder.
    """
    def __init__(self, distance, voltage):
        self.distance = distance
        self.voltage = voltage

    def __str__(self):
        return "Rangefinder: distance={}, voltage={}".format(self.distance, self.voltage)

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
    `Copter <http://copter.ardupilot.com/wiki/flying-arducopter/flight-modes/>`_,
    `Plane <http://plane.ardupilot.com/wiki/flying/flight-modes/>`_,
    `Rover <http://rover.ardupilot.com/wiki/configuration-2/#mode_meanings>`_). If an unsupported mode is set the script
    will raise a ``KeyError`` exception.

    The :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>` attribute can be queried for the current mode. 
    The code snippet below shows how to observe changes to the mode and then read the value:

    .. code:: python

        #Callback definition for mode observer
        def mode_callback(self, attr_name):
            print "Vehicle Mode", self.mode

        #Add observer callback for attribute `mode`
        vehicle.on_attribute('mode', mode_callback)

    The code snippet below shows how to change the vehicle mode to AUTO:

    .. code:: python

        # Set the vehicle into auto mode
        vehicle.mode = VehicleMode("AUTO")

    For more information on getting/setting/observing the :py:attr:`Vehicle.mode <dronekit.lib.Vehicle.mode>` 
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

class HasObservers(object):
    def __init__(self):
        # A mapping from attr_name to a list of observers
        self.__observers = {}

    """
    Provides callback based notification on attribute changes.

    The argument list for observer is ``observer(object, attr_name)``.
    """
    def on_attribute(self, attr_name, observer):
        """
        Add an attribute listener.

        The ``observer`` callback function is called with the ``self`` and ``attr_name`` 
        arguments:
        
        * The ``attr_name`` (attribute name) can be used to infer which attribute has triggered
          if the same callback is used for watching several attributes.
        * The ``self`` attribute is the associated :py:class:`Vehicle`. If needed, it can be compared
          to a global vehicle handle to implement vehicle-specific callback handling.

        The example below shows how to get callbacks for location changes:

        .. code:: python

            #Callback to print the location in global and local frames
            def location_callback(self, attr_name):
                print "Location (Global): ", self.location.global_frame
                print "Location (Local): ", self.location.local_frame

            #Add observer for the vehicle's current location
            vehicle.on_attribute('location', location_callback)

          
        .. note::

            The callback function is invoked every time the associated attribute is updated 
            from the vehicle (the attribute value may not have *changed*).
            The callback can be removed using :py:func:`remove_attribute_listener`.            
        
        :param String attr_name: The attribute to watch.
        :param observer: The callback to invoke when a change in the attribute is detected.

        """
        l = self.__observers.get(attr_name)
        if l is None:
            l = []
            self.__observers[attr_name] = l
        if not observer in l:
            l.append(observer)

    def remove_attribute_listener(self, attr_name, observer):
        """
        Remove an attribute listener (observer) that was previously added using :py:func:`on_attribute`.

        For example, the following line would remove a previously added vehicle 'global_frame' 
        observer called ``location_callback``:

        .. code:: python

            vehicle.remove_attribute_listener('global_frame', location_callback)

        :param String attr_name: The attribute name that is to have an observer removed.
        :param observer: The callback function to remove.

        """
        l = self.__observers.get(attr_name)
        if l is not None:
            l.remove(observer)
            if len(l) == 0:
                del self.__observers[attr_name]

    def _notify_attribute_listeners(self, attr_name):
        """
        Internal function. Do not use.

        This method calls observers when the named attribute has changed.

        .. INTERNAL NOTE: (For subclass use only)
        """
        for fn in self.__observers.get(attr_name, []):
            fn(self, attr_name)
        for fn in self.__observers.get('*', []):
            fn(self, attr_name)

    def attribute_listener(self, name):
        """
        Decorator for attribute listeners.
        
        This is used to create/define new attribute listenters. After using this method you can 
        register an observer for the attribute using :py:func:`on_attribute`.
        
        .. note:: 
        
            The in-built attributes already have listeners (created using this method). The
            method is public so that you can use it to add listeners to *new* attributes. 
        
        The example below shows how you can create a listener for the attitude attribute.

        .. code:: python

            @vehicle.attribute_listener('attitude')
            def attitude_listener(self, name, msg):
                pass
        """
        def decorator(fn):
            if isinstance(name, list):
                for n in name:
                    self.on_attribute(n, fn)
            else:
                self.on_attribute(name, fn)
        return decorator

class Vehicle(HasObservers):
    """
    The main vehicle API

    Asynchronous notification on change of vehicle state is available by registering observers (callbacks) for attribute changes.

    Most vehicle state is exposed through python attributes (e.g. ``vehicle.location``). Most of these attributes are
    auto-populated based on the capabilities of the connected autopilot/vehicle.

    Particular autopilots/vehicles may define different attributes from this standard list (extra batteries, GPIOs, etc.)
    However if a standard attribute is defined it must follow the rules specified below.

    **Autopilot specific attributes & types:**

    To prevent name clashes the following naming convention should be used:

    * ``ap_<name>`` - For autopilot specific parameters (apm 2.5, pixhawk etc.). For example "ap_pin5_mode" and "ap_pin5_value".
    * ``user_<name>`` - For user specific parameters

    **Standard attributes & types:**

    .. py:attribute:: location.global_frame

        Current :py:class:`LocationGlobal`.

    .. py:attribute:: location.local_frame

        Current :py:class:`LocationLocal`.

    .. py:attribute:: attitude

        Current vehicle :py:class:`Attitude` (pitch, yaw, roll).

    .. py:attribute:: velocity

        Current velocity as a three element list ``[ vx, vy, vz ]`` (in meter/sec).

    .. py:attribute:: mode

        This attribute is used to get and set the current flight mode (:py:class:`VehicleMode`).

    .. py:attribute:: airspeed

        Current airspeed in metres/second (``double``).

        .. todo:: FIXME: Should airspeed value move somewhere else from "Standard attributes & types" table?

    .. py:attribute:: groundspeed

        Groundspeed in metres/second (``double``).

    .. py:attribute:: gps_0

        GPS position information (:py:class:`GPSInfo`).

    .. py:attribute:: armed

        This attribute can be used to get and set the ``armed`` state of the vehicle (``boolean``).

        The code below shows how to read the state, and to arm/disam the vehicle:

        .. code:: python

            # Print the armed state for the vehicle
            print "Armed: %s" % vehicle.armed

            # Disarm the vehicle
            vehicle.armed = False

            # Arm the vehicle
            vehicle.armed = True

    .. py:attribute:: mount_status

        Current status of the camera mount (gimbal) as a three element list: ``[ pitch, yaw, roll ]``.

        The values in the list are set to ``None`` if no mount is configured.

    .. py:attribute:: battery

        Current system :py:class:`Battery` status.

    .. py:attribute:: rangefinder

        :py:class:`Rangefinder` distance and voltage values.

    .. py:attribute:: channel_override

        .. warning::

            RC override may be useful for simulating user input and when implementing certain types of joystick control.
            It should not be used for direct control of vehicle channels unless there is no other choice!

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

            # Cancel override on channel 1 and 4 by sending 0
            vehicle.channel_override = { "1" : 0, "4" : 0 }

        .. versionchanged:: 1.0

            This update replaces ``rc_override`` with ``channel_override``/``channel_readback`` documentation.

        .. todo:: Add note to the examples/guide like warning above not to use this mechanism except as intended:

            https://github.com/dronekit/dronekit-python/issues/72

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
        :py:attr:`channel_override <dronekit.lib.Vehicle.channel_override>`). Dictionary entries have the format ``channelName -> value``.

        For example, the returned dictionary might look like this:

        .. code:: python

            RC readback: {'1': 1500, '3': 1000, '2': 1500, '5': 1800, '4': 1500, '7': 1000, '6': 1000, '8': 1800} ? Dictionary () (read only)

    .. todo:: In V2, there may be ardupilot specific attributes & types (as in the introduction). If so, text below might be useful.

        **Autopilot specific attributes & types:**

        .. py:attribute:: ap_pin5_mode

            string (adc, dout, din)

        .. py:attribute:: ap_pin5_value

            ? double (0, 1, 2.3 etc...)

    .. todo:: Add waypoint_home attribute IF this is added: https://github.com/dronekit/dronekit-python/issues/105

    """

    def __init__(self, handler):
        super(Vehicle, self).__init__()

        self._handler = handler
        self._master = handler.master

        # Cache all updated attributes for wait_ready.
        # By default, we presume all "commands" are loaded.
        self._ready_attrs = set(['commands'])

        # Default parameters when calling wait_ready() or wait_ready(True).
        self._default_ready_attrs = ['parameters', 'gps_0', 'armed', 'mode', 'attitude']

        @self.attribute_listener('*')
        def listener(_, name):
            self._ready_attrs.add(name)

        # Attaches message listeners.
        self._message_listeners = dict()

        @handler.message_listener
        def listener(_, msg):
            self._notify_message_listeners(msg.get_type(), msg)

        self._lat = None
        self._lon = None
        self._vx = None
        self._vy = None
        self._vz = None

        @self.message_listener('GLOBAL_POSITION_INT')
        def listener(self, name, m):
            (self._lat, self._lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            self._notify_attribute_listeners('location')
            (self._vx, self._vy, self._vz) = (m.vx / 100.0, m.vy / 100.0, m.vz / 100.0)
            self._notify_attribute_listeners('velocity')

        self._north = None
        self._east = None
        self._down = None

        @self.message_listener('LOCAL_POSITION_NED')
        def listener(self, name, m):
            self._north = m.x
            self._east = m.y
            self._down = m.z
            self._notify_attribute_listeners('local_position')

        self._pitch = None
        self._yaw = None
        self._roll = None
        self._pitchspeed = None
        self._yawspeed = None
        self._rollspeed = None

        @self.message_listener('ATTITUDE')
        def listener(self, name, m):
            self._pitch = m.pitch
            self._yaw = m.yaw
            self._roll = m.roll
            self._pitchspeed = m.pitchspeed
            self._yawspeed = m.yawspeed
            self._rollspeed = m.rollspeed
            self._notify_attribute_listeners('attitude')

        self._heading = None
        self._alt = None
        self._airspeed = None
        self._groundspeed = None

        @self.message_listener('VFR_HUD')
        def listener(self, name, m):
            self._heading = m.heading
            self._notify_attribute_listeners('heading')
            self._alt = m.alt
            self._notify_attribute_listeners('location')
            self._airspeed = m.airspeed
            self._notify_attribute_listeners('airspeed')
            self._groundspeed = m.groundspeed
            self._notify_attribute_listeners('groundspeed')

        self._rngfnd_distance = None
        self._rngfnd_voltage = None

        @self.message_listener('RANGEFINDER')
        def listener(self, name, m):
            self._rngfnd_distance = m.distance
            self._rngfnd_voltage = m.voltage
            self._notify_attribute_listeners('rangefinder')

        self._mount_pitch = None
        self._mount_yaw = None
        self._mount_roll = None

        @self.message_listener('MOUNT_STATUS')
        def listener(self, name, m):
            self._mount_pitch = m.pointing_a / 100
            self._mount_roll = m.pointing_b / 100
            self._mount_yaw = m.pointing_c / 100
            self._notify_attribute_listeners('mount')

        self._rc_readback = {}

        @self.message_listener('RC_CHANNELS_RAW')
        def listener(self, name, m):
            def set_rc(chnum, v):
                '''Private utility for handling rc channel messages'''
                # use port to allow ch nums greater than 8
                self._rc_readback[str(m.port * 8 + chnum)] = v

            set_rc(1, m.chan1_raw)
            set_rc(2, m.chan2_raw)
            set_rc(3, m.chan3_raw)
            set_rc(4, m.chan4_raw)
            set_rc(5, m.chan5_raw)
            set_rc(6, m.chan6_raw)
            set_rc(7, m.chan7_raw)
            set_rc(8, m.chan8_raw)

        self._voltage = None
        self._current = None
        self._level = None

        @self.message_listener('SYS_STATUS')
        def listener(self, name, m):
            self._voltage = m.voltage_battery
            self._current = m.current_battery
            self._level = m.battery_remaining
            self._notify_attribute_listeners('battery')

        self._eph = None
        self._epv = None
        self._satellites_visible = None
        self._fix_type = None  # FIXME support multiple GPSs per vehicle - possibly by using componentId

        @self.message_listener('GPS_RAW_INT')
        def listener(self, name, m):
            self._eph = m.eph
            self._epv = m.epv
            self._satellites_visible = m.satellites_visible
            self._fix_type = m.fix_type
            self._notify_attribute_listeners('gps_0')

        self._current_waypoint = 0

        @self.message_listener(['WAYPOINT_CURRENT', 'MISSION_CURRENT'])
        def listener(self, name, m):
            self._current_waypoint = m.seq

        self._ekf_poshorizabs = False
        self._ekf_constposmode = False
        self._ekf_predposhorizabs = False

        @self.message_listener('EKF_STATUS_REPORT')
        def listener(self, name, m):
            # boolean: EKF's horizontal position (absolute) estimate is good
            self._ekf_poshorizabs = (m.flags & ardupilotmega.EKF_POS_HORIZ_ABS) > 0
            # boolean: EKF is in constant position mode and does not know it's absolute or relative position
            self._ekf_constposmode = (m.flags & ardupilotmega.EKF_CONST_POS_MODE) > 0
            # boolean: EKF's predicted horizontal position (absolute) estimate is good
            self._ekf_predposhorizabs = (m.flags & ardupilotmega.EKF_PRED_POS_HORIZ_ABS) > 0

            self._notify_attribute_listeners('ekf_ok')

        self._flightmode = 'AUTO'
        self._armed = False
        self._system_status = None

        @self.message_listener('HEARTBEAT')
        def listener(self, name, m):
            self._armed = (m.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            self._notify_attribute_listeners('armed')
            self._flightmode = {v: k for k, v in self._master.mode_mapping().items()}[m.custom_mode]
            self._system_status = m.system_status
            self._notify_attribute_listeners('mode')

        # Waypoints.

        self._wploader = mavwp.MAVWPLoader()
        self._wp_loaded = True
        self._wp_uploaded = None
        self._wpts_dirty = False
        self._commands = CommandSequence(self)

        @self.message_listener(['WAYPOINT_COUNT','MISSION_COUNT'])
        def listener(self, name, msg):
            if not self._wp_loaded:
                self._wploader.clear()
                self._wploader.expected_count = msg.count
                self._master.waypoint_request_send(0)

        @self.message_listener(['WAYPOINT', 'MISSION_ITEM'])
        def listener(self, name, msg):
            if not self._wp_loaded:
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
                        self._notify_attribute_listeners('commands')

        # Waypoint send to master
        @self.message_listener(['WAYPOINT_REQUEST', 'MISSION_REQUEST'])
        def listener(self, name, msg):
            if self._wp_uploaded != None:
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
        self._params_last = time.time() # Last new param.
        self._params_duration = start_duration
        self._parameters = Parameters(self)

        @handler.loop_listener
        def listener(_):
            # Check the time duration for last "new" params exceeds watchdog.
            if self._params_start:
                if None not in self._params_set and not self._params_loaded:
                    self._params_loaded = True
                    self._notify_attribute_listeners('parameters')

                if not self._params_loaded and time.time() - self._params_last > self._params_duration:
                    c = 0
                    for i, v in enumerate(self._params_set):
                        if v == None:
                            self._master.mav.param_request_read_send(0, 0, '', i)
                            c += 1
                            if c > 50:
                                break
                    self._params_duration = repeat_duration
                    self._params_last = time.time()

        @self.message_listener(['PARAM_VALUE'])
        def listener(self, name, msg):
            # If we discover a new param count, assume we
            # are receiving a new param set.
            if self._params_count != msg.param_count:
                self._params_loaded = False
                self._params_start = True
                self._params_count = msg.param_count
                self._params_set = [None]*msg.param_count

            # Attempt to set the params. We throw an error
            # if the index is out of range of the count or
            # we lack a param_id.
            try:
                if msg.param_index < msg.param_count and msg:
                    if self._params_set[msg.param_index] == None:
                        self._params_last = time.time()
                        self._params_duration = start_duration
                    self._params_set[msg.param_index] = msg
                self._params_map[msg.param_id] = msg.param_value
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

        @handler.loop_listener
        def listener(_):
            # Send 1 heartbeat per second
            if time.time() - self._heartbeat_lastsent > 1:
                self._master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                self._heartbeat_lastsent = time.time()

            # Timeouts.
            if self._heartbeat_started:
                if self._heartbeat_error and self._heartbeat_error > 0 and time.time() - self._heartbeat_lastreceived > self._heartbeat_error:
                    raise Exception('>>> No heartbeat in %s seconds, aborting.' % self._heartbeat_error)
                elif time.time() - self._heartbeat_lastreceived > self._heartbeat_warning:
                    if self._heartbeat_timeout == False:
                        errprinter('>>> Link timeout, no heartbeat in last %s seconds' % self._heartbeat_warning)
                        self._heartbeat_timeout = True

        @self.message_listener(['HEARTBEAT'])
        def listener(self, name, msg):
            self._heartbeat_lastreceived = time.time()
            if self._heartbeat_timeout:
                errprinter('>>> ...link restored.')
            self._heartbeat_timeout = False

    def message_listener(self, name):
        """
        Decorator for message listeners.
        
        A decorated message listener is called with three arguments every time the 
        specified message is received: 
        
        * ``self`` - the current vehicle.
        * ``name`` - the name of the message that was intercepted.
        * ``message`` - the actual message, a `pymavlink <http://www.qgroundcontrol.org/mavlink/pymavlink>`_
          `class <https://www.samba.org/tridge/UAV/pymavlink/apidocs/classIndex.html>`_.        

        For example, in the fragment below ``my_method`` will be called for every heartbeat message:
        
        .. code:: python

            @vehicle.message_listener('HEARTBEAT')
            def my_method(self, name, msg):
                pass
                
        :param String name: The name of the message to be intercepted by the decorated listener function.
        """
        def decorator(fn):
            if isinstance(name, list):
                for n in name:
                    self.on_message(n, fn)
            else:
                self.on_message(name, fn)
        return decorator

    def on_message(self, name, fn):
        """
        Adds a message listener.
        """
        name = str(name)
        if name not in self._message_listeners:
            self._message_listeners[name] = []
        if fn not in self._message_listeners[name]:
            self._message_listeners[name].append(fn)

    def remove_message_listener(self, name, fn):
        """
        Removes a message listener (that was added using :py:func:`message_listener`)
        """
        name = str(name)
        if name in self._message_listeners:
            self._message_listeners[name].remove(fn)
            if len(self._message_listeners[name]) == 0:
                del self._message_listeners[name]

    def _notify_message_listeners(self, name, msg):
        for fn in self._message_listeners.get(name, []):
            fn(self, name, msg)
        for fn in self._message_listeners.get('*', []):
            fn(self, name, msg)

    def close(self):
        return self._handler.close()

    def flush(self):
        """
        Call ``flush()`` after :py:func:`adding <CommandSequence.add>` or :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``flush()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.

        .. warning:: 

            This has been replaced by :py:func:`Vehicle.commands.upload() <Vehicle.commands.upload>`.
        """
        return self.commands.upload()

    #
    # Private sugar methods
    #

    @property
    def _mode_mapping(self):
        return self._master.mode_mapping()

    #
    # Operations to support the standard API.
    #

    @property
    def mode(self):
        if not self._flightmode:
            return None
        return VehicleMode(self._flightmode)

    @mode.setter
    def mode(self, v):
        self._master.set_mode(self._mode_mapping[v.name])

    @property
    def location(self):
        # For backward compatibility, this is (itself) a LocationLocal object.
        ret = LocationGlobal(self._lat, self._lon, self._alt, is_relative=False)
        ret.local_frame = LocationLocal(self._north, self._east, self._down)
        ret.global_frame = LocationGlobal(self._lat, self._lon, self._alt, is_relative=False)
        return ret

    @property
    def battery(self):
        return Battery(self._voltage, self._current, self._level)

    @property
    def rangefinder(self):
        return Rangefinder(self._rngfnd_distance, self._rngfnd_voltage)

    @property
    def velocity(self):
        return [ self._vx, self._vy, self._vz ]

    @property
    def attitude(self):
        return Attitude(self._pitch, self._yaw, self._roll)

    @property
    def gps_0(self):
        return GPSInfo(self._eph, self._epv, self._fix_type, self._satellites_visible)

    @property
    def armed(self):
        return self._armed

    @armed.setter
    def armed(self, value):
        if value:
            self._master.arducopter_arm()
        else:
            self._master.arducopter_disarm()

    @property
    def system_status(self):
        return self._system_status

    @property
    def heading(self):
        return self._heading

    @property
    def groundspeed(self):
        return self._groundspeed

    @property
    def airspeed(self):
        return self._airspeed

    @property
    def mount_status(self):
        return [ self._mount_pitch, self._mount_yaw, self._mount_roll ]

    @property
    def ekf_ok(self):
        # legacy check for dronekit-python for solo
        # use same check that ArduCopter::system.pde::position_ok() is using
        if self.armed:
            return self._ekf_poshorizabs and not self._ekf_constposmode
        else:
            return self._ekf_poshorizabs or self._ekf_predposhorizabs

    @property
    def channel_override(self):
        overrides = self.__rc.override
        # Only return entries that have a non zero override
        return dict((str(num + 1), overrides[num]) for num in range(8) if overrides[num] != 0)

    @channel_override.setter
    def channel_override(self, newch):
        overrides = self.__rc.override
        for k, v in newch.iteritems():
            overrides[int(k) - 1] = v
        self.__rc.set_override(overrides)

    @property
    def channel_readback(self):
        return copy.copy(self._rc_readback)

    @property
    def home_location(self):
        """
        The current home location in a :py:class:`LocationGlobal`. 

        This value is initially set by the autopilot as the location of first GPS Lock.
        The attribute has a value of ``None`` until :py:func:`Vehicle.commands` has been downloaded. 
        If the attribute is queried before the home location is set the returned `LocationGlobal` 
        will have zero values for its member attributes.

        .. code-block:: python

            #Connect to a vehicle object (for example, on com14)
            vehicle = connect('com14', wait_ready=True)

            # Download the vehicle waypoints (commands). Wait until download is complete.
            cmds = vehicle.commands
            cmds.download()
            cmds.wait_ready()

            # Get the home location
            home = vehicle.home_location

        The attribute is not writeable or observable.

        """
        loc = self._wploader.wp(0)
        if loc:
            return LocationGlobal(loc.x, loc.y, loc.z, is_relative=False)

    @home_location.setter
    def home_location(self, pos):
        """
        Sets the home location to that of a ``LocationGlobal`` object.

        .. note:: 

            If the GPS values differ heavily from EKF values, setting this value will fail silently.
        """
        self.send_mavlink(self.message_factory.command_long_encode(
            0, 0, # target system, target component
            mavutil.mavlink.MAV_CMD_DO_SET_HOME, # command
            0, # confirmation
            2, # param 1: 1 to use current position, 2 to use the entered values.
            0, 0, 0, # params 2-4
            pos.lat,
            pos.lon,
            pos.alt
            ))

    @property
    def commands(self):
        """
        Gets the editable waypoints for this vehicle (the current "mission").

        This can be used to get, create, and modify a mission. It can also be used for direct control of vehicle position
        (outside missions) using the :py:func:`goto <dronekit.lib.CommandSequence.goto>` method.

        :returns: A :py:class:`CommandSequence` containing the waypoints for this vehicle.
        """
        return self._commands

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle (:py:class:`Parameters <dronekit.lib.Parameters>`).
        """
        return self._parameters

    def send_mavlink(self, message):
        """
        This method is used to send raw MAVLink "custom messages" to the vehicle.

        The function can send arbitrary messages/commands to a vehicle at any time and in any vehicle mode. It is particularly useful for
        controlling vehicles outside of missions (for example, in GUIDED mode).

        The :py:func:`message_factory <dronekit.lib.Vehicle.message_factory>` is used to create messages in the appropriate format.
        Callers do not need to populate sysId/componentId/crc in the packet as the method will take care of that before sending.

        :param message: A ``MAVLink_message`` instance, created using :py:func:`message_factory <dronekit.lib.Vehicle.message_factory>`.
            There is need to specify the system id, component id or sequence number of messages as the API will set these appropriately.
        """
        self._master.mav.send(message)

    @property
    def message_factory(self):
        """
        Returns an object that can be used to create 'raw' MAVLink messages that are appropriate for this vehicle.
        The message can then be sent using :py:func:`send_mavlink(message) <dronekit.lib.Vehicle.send_mavlink>`.

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
        return self._master.mav

    def initialize(self, wait_ready=False, rate=None, heartbeat_timeout=30):
        self._handler.start()

        # Start heartbeat polling.
        start = time.time()
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

        # Wait until board has booted.
        while True:
            if self._flightmode not in [None, 'INITIALISING', 'MAV']:
                break
            time.sleep(0.1)

        # Initialize data stream.
        if rate != None:
            self._master.mav.request_data_stream_send(0, 0,
                                                      mavutil.mavlink.MAV_DATA_STREAM_ALL, rate, 1)

        # Ensure initial parameter download has started.
        while True:
            # This fn actually rate limits itself to every 2s.
            # Just retry with persistence to get our first param stream.
            self._master.param_fetch_all()
            time.sleep(0.1)
            if self._params_count > -1:
                break

    def wait_ready(self, *types, **kwargs):
        timeout = kwargs.get('timeout', 30)
        raise_exception = kwargs.get('raise_exception', True)

        # Vehicle defaults for wait_ready(True) or wait_ready()
        if list(types) == [True] or list(types) == []:
            types = self._default_ready_attrs

        if not all(isinstance(item, basestring) for item in types):
            raise APIException('wait_ready expects one or more string arguments.')

        # Wait for these attributes to have been set.
        await = set(types)
        start = time.time()
        while not await.issubset(self._ready_attrs):
            time.sleep(0.1)
            if time.time() - start > timeout:
                if raise_exception:
                    raise APIException('wait_ready experienced a timeout after %s seconds.' % timeout)
                else:
                    return False

        return True

class Parameters(HasObservers):
    """
    This object is used to get and set the values of named parameters for a vehicle. See the following links for information about
    the supported parameters for each platform: `Copter <http://copter.ardupilot.com/wiki/configuration/arducopter-parameters/>`_,
    `Plane <http://plane.ardupilot.com/wiki/arduplane-parameters/>`_, `Rover <http://rover.ardupilot.com/wiki/apmrover2-parameters/>`_.

    Attribute names are generated automatically based on parameter names.  The example below shows how to get and set the value of a parameter.

    .. code:: python

        # Print the value of the THR_MIN parameter.
        print "Param: %s" % vehicle.parameters['THR_MIN']

        # Change the parameter value to something different.
        vehicle.parameters['THR_MIN']=100

    .. note::

        At time of writing ``Parameters`` does not implement the observer methods, and change notification for parameters
        is not supported.

    .. todo::

        Check to see if observers have been implemented and if so, update the information here, in about, and in Vehicle class:
        https://github.com/dronekit/dronekit-python/issues/107
    """

    def __init__(self, vehicle):
        self._vehicle = vehicle

    def __getitem__(self, name):
        self.wait_ready()
        return self._vehicle._params_map[name]

    def __setitem__(self, name, value):
        self.wait_ready()
        self.set(name, value)

    def get(self, name, wait_ready=True):
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
        value = float(value)
        success = False
        remaining = retries
        while True:
            self._vehicle._master.param_set_send(name.upper(), value)
            tstart = time.time()
            if remaining == 0:
                break
            remaining -= 1
            while time.time() - tstart < 1:
                if name in self._vehicle._params_map and self._vehicle._params_map[name] == value:
                    return True
                time.sleep(0.1)

        if retries > 0:
            errprinter("timeout setting parameter %s to %f" % (name, value))
        return False

    def wait_ready(self, **kwargs):
        """
        Block the calling thread until parameters have been downloaded
        """
        self._vehicle.wait_ready('parameters', **kwargs)

class Command(mavutil.mavlink.MAVLink_mission_item_message):
    """
    A waypoint object.

    This object encodes a single mission item command. The set of commands that are supported by ArduPilot in Copter, Plane and Rover (along with their parameters)
    are listed in the wiki article `MAVLink Mission Command Messages (MAV_CMD) <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/>`_.

    For example, to create a `NAV_WAYPOINT <http://planner.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_nav_waypoint>`_ command:

    .. code:: python

        cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,-34.364114, 149.166022, 30)

    :param target_system: The id number of the message's target system (drone, GSC) within the MAVLink network.
        Set this to zero (broadcast) when communicating with a companion computer.
    :param target_component: The id of a component the message should be routed to within the target system
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

    .. todo:: Confirm if target_sytem, target_component, seq, frame are all handled for you or not. If not, check that these are correct.
    .. todo:: FIXME: Command class - for now we just inherit the standard MAVLink mission item contents.
    """
    pass

class CommandSequence(object):
    """
    A sequence of vehicle waypoints (a "mission").

    Operations include 'array style' indexed access to the various contained waypoints.

    The current commands/mission for a vehicle are accessed using the :py:attr:`Vehicle.commands <dronekit.lib.Vehicle.commands>` attribute.
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

    .. py:function:: takeoff(altitude)

        .. note:: This function should only be used on Copter vehicles.

        Take off and fly the vehicle to the specified altitude (in metres) and then wait for another command.

        The vehicle must be in ``GUIDED`` mode and armed before this is called.

        There is no mechanism for notification when the correct altitude is reached, and if another command arrives
        before that point (e.g. :py:func:`goto`) it will be run instead.

        .. warning::

            Apps should code to ensure that the vehicle will reach a safe altitude before other commands are executed.
            A good example is provided in the guide topic :ref:`taking-off`.

        :param altitude: Target height, in metres.

        .. todo:: This is a hack. The actual function should be defined here. See https://github.com/dronekit/dronekit-python/issues/64
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

    def takeoff(self, alt=None):
        if alt is not None:
            altitude = float(alt)
            if math.isnan(alt) or math.isinf(alt):
                raise ValueError("Altitude was NaN or Infinity. Please provide a real number")
            self._vehicle._master.mav.command_long_send(0, 0,
                                                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                        0, 0, 0, 0, 0, 0, 0,
                                                        altitude)

    def goto(self, l):
        '''
        Go to a specified global location (:py:class:`LocationGlobal`).

        The method will change the :py:class:`VehicleMode` to ``GUIDED`` if necessary.

        .. code:: python

            # Set mode to guided - this is optional as the goto method will change the mode if needed.
            vehicle.mode = VehicleMode("GUIDED")

            # Set the LocationGlobal to head towards
            a_location = LocationGlobal(-34.364114, 149.166022, 30, is_relative=True)
            vehicle.commands.goto(a_location)

        :param LocationGlobal location: The target location.
        '''
        if l.is_relative:
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        else:
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL
        self._vehicle._master.mav.mission_item_send(0, 0, 0,
                                                    frame,
                                                    mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                                    2, 0, 0, 0, 0, 0,
                                                    l.lat, l.lon, l.alt)

    def clear(self):
        '''
        Clear the command list. 

        This command will be sent to the vehicleonly after you call :py:func:`upload() <Vehicle.commands.upload>`.
        '''

        # Add home point again.
        self.wait_ready()
        home = self._vehicle._wploader.wp(0)
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

    def upload(self):
        """
        Call ``upload()`` after :py:func:`adding <CommandSequence.add>` or :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``upload()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.
        """
        if self._vehicle._wpts_dirty:
            self._vehicle._master.waypoint_clear_all_send()
            if self._vehicle._wploader.count() > 0:
                self._vehicle._wp_uploaded = [False]*self._vehicle._wploader.count()
                self._vehicle._master.waypoint_count_send(self._vehicle._wploader.count())
                while False in self._vehicle._wp_uploaded:
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
            return [self[ii] for ii in xrange(*index.indices(len(self)))]
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
