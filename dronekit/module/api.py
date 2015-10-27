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

class MPVehicle(Vehicle):
    def __init__(self, module):
        super(MPVehicle, self).__init__()
        self.__module = module
        self._parameters = Parameters(module)
        self._waypoints = None
        self.wpts_dirty = False

    def close(self):
        return self.__module.close()

    def flush(self):
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
        The (editable) waypoints for this vehicle.
        """
        if(self._waypoints is None):  # We create the wpts lazily (because this will start a fetch)
            self._waypoints = CommandSequence(self.__module)
        return self._waypoints

    def send_mavlink(self, message):
        self.__module.fix_targets(message)
        self.__module.master.mav.send(message)

    @property
    def message_factory(self):
        """
        Returns an object that can be used to create 'raw' mavlink messages that are appropriate for this vehicle.
        These message types are defined in the central Mavlink github repository.  For example, a Pixhawk understands
        the following messages: (from https://github.com/mavlink/mavlink/blob/master/message_definitions/v1.0/pixhawk.xml).

          <message id="153" name="IMAGE_TRIGGER_CONTROL">
               <field type="uint8_t" name="enable">0 to disable, 1 to enable</field>
          </message>

        The name of the factory method will always be the lower case version of the message name with _encode appended.
        Each field in the xml message definition must be listed as arguments to this factory method.  So for this example
        message, the call would be:

        msg = vehicle.message_factory.image_trigger_control_encode(True)
        vehicle.send_mavlink(msg)
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
