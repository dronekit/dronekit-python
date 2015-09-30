import os
import time
import threading
import traceback
import logging
import math
from pymavlink import mavutil
from droneapi.lib import APIConnection, Vehicle, VehicleMode, Location, \
    Attitude, GPSInfo, Parameters, CommandSequence, APIException, Battery, \
    Rangefinder

# Enable logging here (until this code can be moved into mavproxy)
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class MPParameters(Parameters):
    """
    See Parameters baseclass for documentation.

    FIXME - properly publish change notification
    """

    def __init__(self, module):
        self.__module = module

    def __getitem__(self, name):
        self.wait_valid()
        return self.__module.mav_param[name]

    def __setitem__(self, name, value):
        self.wait_valid()
        self.__module.mpstate.functions.param_set(name, value)

    def wait_valid(self):
        '''Block the calling thread until parameters have been downloaded'''
        # FIXME this is a super crufty spin-wait, also we should give the user the option of specifying a timeout
        pstate = self.__param.pstate
        while (pstate.mav_param_count == 0 or len(pstate.mav_param_set) != pstate.mav_param_count) and not self.__module.api.exit:
            time.sleep(0.200)

    @property
    def __param(self):
        return self.__module.module('param')

class MPCommandSequence(CommandSequence):
    """
    See CommandSequence baseclass for documentation.
    """

    def __init__(self, module):
        self.__module = module

    def download(self):
        '''Download all waypoints from the vehicle'''
        self.wait_valid()
        self.__wp.fetch()
        # BIG FIXME - wait for full wpt download before allowing any of the accessors to work

    def wait_valid(self):
        '''Block the calling thread until waypoints have been downloaded'''
        # FIXME this is a super crufty spin-wait, also we should give the user the option of specifying a timeout
        while (self.__wp.wp_op is not None) and not self.__module.api.exit:
            time.sleep(0.200)

    def takeoff(self, alt=None):
        if alt is not None:
            altitude = float(alt)
            if math.isnan(alt) or math.isinf(alt):
                raise ValueError("Altitude was NaN or Infinity. Please provide a real number")
            self.__module.master.mav.command_long_send(self.__module.target_system,
                                                    self.__module.target_component,
                                                    mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                    0, 0, 0, 0, 0, 0, 0,
                                                    altitude)

    def goto(self, l):
        if l.is_relative:
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        else:
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL
        self.__module.master.mav.mission_item_send(self.__module.target_system,
                                               self.__module.target_component,
                                               0,
                                               frame,
                                               mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                               2, 0, 0, 0, 0, 0,
                                               l.lat, l.lon, l.alt)

    def clear(self):
        '''Clears the command list'''
        self.wait_valid()
        self.__wp.wploader.clear()
        self.__module.vehicle.wpts_dirty = True

    def add(self, cmd):
        '''Add a new command at the end of the command list'''
        self.wait_valid()
        self.__module.fix_targets(cmd)
        self.__wp.wploader.add(cmd, comment = 'Added by DroneAPI')
        self.__module.vehicle.wpts_dirty = True

    @property
    def __wp(self):
        return self.__module.module('wp')

    @property
    def count(self):
        return self.__wp.wploader.count()

    @property
    def next(self):
        """
        Currently active waypoint number

        (implementation provided by subclass)
        """
        return self.__module.last_waypoint

    @next.setter
    def next(self, index):
        self.__module.master.waypoint_set_current_send(index)

    def __getitem__(self, index):
        return self.__wp.wploader.wp(index)

    def __setitem__(self, index, value):
        self.__wp.wploader.set(value, index)
        self.__module.vehicle.wpts_dirty = True

class MPVehicle(Vehicle):
    def __init__(self, module):
        super(MPVehicle, self).__init__()
        self.__module = module
        self._parameters = MPParameters(module)
        self._waypoints = None
        self.wpts_dirty = False

    def flush(self):
        if self.wpts_dirty:
            self.__module.module('wp').send_all_waypoints()
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
        return VehicleMode(self.__module.status.flightmode)

    @mode.setter
    def mode(self, v):
        self.wait_init() # We must know vehicle type before this operation can work
        self.__master.set_mode(self.__mode_mapping[v.name])

    @property
    def location(self):
        return Location(self.__module.lat, self.__module.lon, self.__module.alt, is_relative=False)

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
        return self.__module.mpstate.status.armed

    @armed.setter
    def armed(self, value):
        if value:
            self.__master.arducopter_arm()
        else:
            self.__master.arducopter_disarm()

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
    def __rc(self):
        return self.__module.module('rc')

    @property
    def commands(self):
        """
        The (editable) waypoints for this vehicle.
        """
        if(self._waypoints is None):  # We create the wpts lazily (because this will start a fetch)
            self._waypoints = MPCommandSequence(self.__module)
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


class MPAPIConnection(APIConnection):
    """
    A small private version of the APIConnection class

    In Mavproxy you probably just want to call get_vehicles
    """
    def __init__(self, module):
        self.__vehicle = MPVehicle(module)

    def get_vehicles(self, query=None):
        return [ self.__vehicle ]

class APIThread(threading.Thread):
    def __init__(self, module, fn, description):
        super(APIThread, self).__init__()
        self.module = module
        self.description = description
        self.exit = False  # Python has no standard way to kill threads, this allows
        self.fn = fn
        self.thread_num = module.next_thread_num
        module.next_thread_num = module.next_thread_num + 1
        self.daemon = True  # For now I think it is okay to let mavproxy exit if api clients are still running
        self.start()
        self.name = "APIThread-%s" % self.thread_num
        self.module.thread_add(self)

        # DroneAPI might generate many commands, which in turn generate ots of acks and status text, in the interest of speed we ignore processing those messages
        try:
            self.module.mpstate.rx_blacklist.add('COMMAND_ACK')
            self.module.mpstate.rx_blacklist.add('STATUSTEXT')
        except:
            pass # Silently work with old mavproxies

    def kill(self):
        """Ask the thread to exit.  The thread must check threading.current_thread().exit periodically"""
        print("Asking %s to exit..." % self.name)
        self.exit = True

    def run(self):
        try:
            self.fn()
            print("%s exiting..." % self.name)
        except Exception as e:
            print("Exception in %s: %s" % (self.name, str(e)))
            traceback.print_exc()

        try:
            self.module.mpstate.rx_blacklist.remove('COMMAND_ACK')
            self.module.mpstate.rx_blacklist.remove('STATUSTEXT')
        except:
            pass # Silently work with old mavproxies

        # Remove all observers.
        self.module.vehicle.remove_all_observers()
        self.module.vehicle.unset_mavlink_callback()

        self.module.thread_remove(self)

    def __str__(self):
        return "%s: %s" % (self.thread_num, self.description)
