import os
import time
import threading
import traceback
import logging
import math
from pymavlink import mavutil
from dronekit.lib import Vehicle, VehicleMode, LocationLocal, \
    LocationGlobal, Attitude, GPSInfo, Parameters, CommandSequence, \
    APIException, Battery, Rangefinder

# Enable logging here (until this code can be moved into mavproxy)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

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

    def __init__(self, module):
        super(Vehicle, self).__init__()
        self.mavrx_callback = None
        self.__module = module
        self._parameters = Parameters(module)
        self._waypoints = None
        self.wpts_dirty = False

    def close(self):
        return self.__module.close()

    def flush(self):
        """
        Call ``flush()`` after :py:func:`adding <CommandSequence.add>` or :py:func:`clearing <CommandSequence.clear>` mission commands.

        After the return from ``flush()`` any writes are guaranteed to have completed (or thrown an
        exception) and future reads will see their effects.
        """
        if self.wpts_dirty:
            self.__module.send_all_waypoints()
            self.wpts_dirty = False

    #
    # Private sugar methods
    #

    @property
    def __master(self):
        return self.__module.master

    @property
    def __mode_mapping(self):
        return self.__master.mode_mapping()

    #
    # Operations to support the standard API (FIXME - possibly/probably this
    # will move into a private dict of getter/setter tuples (invisible to the API consumer).
    #

    @property
    def mode(self):
        self.wait_init() # We must know vehicle type before this operation can work
        return self.__get_mode()

    def __get_mode(self):
        """Private method to read current vehicle mode without polling"""
        return VehicleMode(self.__module.flightmode)

    @mode.setter
    def mode(self, v):
        self.wait_init() # We must know vehicle type before this operation can work
        self.__master.set_mode(self.__mode_mapping[v.name])

    @property
    def location(self):
        # For backward compatibility, this is (itself) a LocationLocal object.
        ret = LocationGlobal(self.__module.lat, self.__module.lon, self.__module.alt, is_relative=False)
        ret.local_frame = LocationLocal(self.__module.north, self.__module.east, self.__module.down)
        ret.global_frame = LocationGlobal(self.__module.lat, self.__module.lon, self.__module.alt, is_relative=False)
        return ret

    @property
    def battery(self):
        return Battery(self.__module.voltage, self.__module.current, self.__module.level)

    @property
    def rangefinder(self):
        return Rangefinder(self.__module.rngfnd_distance, self.__module.rngfnd_voltage)

    @property
    def velocity(self):
        return [ self.__module.vx, self.__module.vy, self.__module.vz ]

    @property
    def attitude(self):
        return Attitude(self.__module.pitch, self.__module.yaw, self.__module.roll)

    @property
    def gps_0(self):
        return GPSInfo(self.__module.eph, self.__module.epv, self.__module.fix_type, self.__module.satellites_visible)

    @property
    def armed(self):
        return self.__module.armed

    @armed.setter
    def armed(self, value):
        if value:
            self.__master.arducopter_arm()
        else:
            self.__master.arducopter_disarm()

    @property
    def system_status(self):
        return self.__module.system_status

    @property
    def groundspeed(self):
        return self.__module.groundspeed

    @property
    def airspeed(self):
        return self.__module.airspeed

    @property
    def mount_status(self):
        return [ self.__module.mount_pitch, self.__module.mount_yaw, self.__module.mount_roll ]

    @property
    def ekf_ok(self):
        return self.__module.ekf_ok

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
        return self.__module.rc_readback

    @property
    def commands(self):
        """
        Gets the editable waypoints for this vehicle (the current "mission").

        This can be used to get, create, and modify a mission. It can also be used for direct control of vehicle position
        (outside missions) using the :py:func:`goto <dronekit.lib.CommandSequence.goto>` method.

        :returns: A :py:class:`CommandSequence` containing the waypoints for this vehicle.
        """
        if(self._waypoints is None):  # We create the wpts lazily (because this will start a fetch)
            self._waypoints = CommandSequence(self.__module)
        return self._waypoints

    @property
    def parameters(self):
        """
        The (editable) parameters for this vehicle (:py:class:`Parameters <dronekit.lib.Parameters>`).
        """
        return self._parameters

    def unset_mavlink_callback(self):
        """
        Clears the asynchronous notification added by :py:func:`set_mavlink_callback <dronekit.lib.Vehicle.set_mavlink_callback>`.

        The code snippet below shows how to set, then clear, a MAVLink callback function.

        .. code:: python

            # Set MAVLink callback handler (after getting Vehicle instance)
            vehicle.set_mavlink_callback(mavrx_debug_handler)

            # Remove the MAVLink callback handler. Callback will not be
            # called after this point.
            vehicle.unset_mavlink_callback()
        """
        self.mavrx_callback = None

    def set_mavlink_callback(self, callback):
        """
        Provides asynchronous notification when any MAVLink packet is received by this vehicle.

        Only a single callback can be set. :py:func:`unset_mavlink_callback <dronekit.lib.Vehicle.unset_mavlink_callback>` removes the callback.

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

        :param callback: The callback function to be invoked when a raw MAVLink message is received.

        """
        self.mavrx_callback = callback

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
        self.__module.fix_targets(message)
        self.__module.master.mav.send(message)

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
        return self.__module.master.mav

    def wait_init(self):
        """Wait for the vehicle to exit the initializing step"""
        timeout = 30
        pollinterval = 0.2
        for i in range(0, int(timeout / pollinterval)):
            # Don't let the user try to fly while the board is still booting
            mode = self.__get_mode().name
            # print "mode is", mode
            if mode != "INITIALISING" and mode != "MAV":
                return

            time.sleep(pollinterval)
        raise APIException("Vehicle did not complete initialization")

    def on_message(self, name, fn):
        def handler(state, name, m):
            return fn(self, name, m)
        return self.__module.on_message(name, handler)
