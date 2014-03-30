import time
import threading
import traceback
from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module
from droneapi.lib import APIConnection, Vehicle, VehicleMode, Location, \
    Attitude, GPSInfo, Parameters, CommandSequence

"""
fixme do follow me example
fixme make mission work
"""

class MPParameters(Parameters):
    """
    See Parameters baseclass for documentation.

    FIXME - properly publish change notification
    """

    def __init__(self, module):
        self.__module = module

    def __getitem__(self, name):
        return self.__module.mav_param[name]

    def __setitem__(self, name, value):
        self.__module.mpstate.functions.param_set(name, value)

class MPCommandSequence(CommandSequence):
    """
    See CommandSequence baseclass for documentation.
    """

    def __init__(self, module):
        self.__module = module

    def download(self):
        '''Download all waypoints from the vehicle'''
        self.__wp.fetch()
        # BIG FIXME - wait for full wpt download before allowing any of the accessors to work

    def wait_valid(self):
        '''Block the calling thread until waypoints have been downloaded'''
        # FIXME this is a super crufty spin-wait, also we should give the user the option of specifying a timeout
        print 'waiting for download'
        while (self.__wp.wp_op is not None) and not self.__module.api.exit:
            time.sleep(0.200)

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

    @property
    def __wp(self):
        return self.__module.module('wp')

    @property
    def count(self):
        return self.__wp.wploader.count()

    @property
    def next(self):
        return None

    @next.setter
    def next(self, index):
        self.__module.master.waypoint_set_current_send(index)

    def __getitem__(self, index):
        return self.__wp.wploader.wp(index)

    def __setitem__(self, index, value):
        self.__wp.wploader.set(value, index)
        # BIG FIXME - mark as dirty/send on next flush

class MPVehicle(Vehicle):
    def __init__(self, module):
        self.__module = module
        self._parameters = MPParameters(module)
        self._waypoints = None

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
        return VehicleMode(self.__module.status.flightmode)

    @mode.setter
    def mode(self, v):
        self.__master.set_mode(self.__mode_mapping[v.name])

    @property
    def location(self):
        return Location(self.__module.lat, self.__module.lon, self.__module.alt)

    @property
    def attitude(self):
        return Attitude(self.__module.pitch, self.__module.yaw, self.__module.roll)

    @property
    def gps_0(self):
        return GPSInfo(self.__module.eph, self.__module.epv, self.__module.fix_type, self.__module.satellites_visible)

    @property
    def commands(self):
        """
        The (editable) waypoints for this vehicle.
        """
        if(self._waypoints is None):  # We create the wpts lazily (because this will start a fetch)
            self._waypoints = MPCommandSequence(self.__module)
        return self._waypoints

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

    def kill(self):
        """Ask the thread to exit.  The thread must check threading.current_thread().exit periodically"""
        print "Asking %s to exit..." % self.name
        self.exit = True

    def run(self):
        try:
            self.fn()
            print("%s exiting..." % self.name)
        except Exception as e:
            print("Exception in %s: %s" % (self.name, str(e)))
            traceback.print_exc()
        self.module.thread_remove(self)

    def __str__(self):
        return "%s: %s" % (self.thread_num, self.description)

class APIModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(APIModule, self).__init__(mpstate, "api")
        self.add_command('api', self.cmd_api, "API commands", [ "<list>", "<start> (FILENAME)", "<stop> [THREAD_NUM]" ])
        self.api = MPAPIConnection(self)
        self.vehicle = self.api.get_vehicles()[0]
        self.lat = None
        self.lon = None
        self.alt = None

        self.airspeed = None
        self.groundspeed = None

        self.pitch = None
        self.yaw = None
        self.roll = None

        self.eph = None
        self.epv = None
        self.satellites_visible = None
        self.fix_type = None  # FIXME support multiple GPSs per vehicle - possibly by using componentId

        self.next_thread_num = 0  # Monotonically increasing
        self.threads = {}  # A map from int ID to thread object
        print("DroneAPI loaded")

    def __on_change(self, *args):
        for a in args:
            self.vehicle.notify_observers(a)

    def unload(self):
        """We ask any api threads to exit"""
        for t in self.threads.values():
            t.kill()
        for t in self.threads.values():
            t.join(5)
            if t.is_alive():
                print "WARNING: Timed out waiting for %s to exit." % t

    def mavlink_packet(self, m):
        if m.get_type() == 'GPS_RAW':
            (self.lat, self.lon) = (m.lat, m.lon)
            self.__on_change('location')
        elif m.get_type() == 'GPS_RAW_INT':
            (self.lat, self.lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            self.eph = m.eph
            self.epv = m.epv
            self.satellites_visible = m.satellites_visible
            self.fix_type = m.fix_type
            self.__on_change('location', 'gps_0')
        elif m.get_type() == "VFR_HUD":
            self.heading = m.heading
            self.alt = m.alt
            self.airspeed = m.airspeed
            self.groundspeed = m.groundspeed
            self.__on_change('location', 'airspeed', 'groundspeed')
        elif m.get_type() == "ATTITUDE":
            self.pitch = m.pitch
            self.yaw = m.yaw
            self.roll = m.roll
            self.__on_change('attitude')

    def thread_remove(self, t):
        del self.threads[t.thread_num]

    def thread_add(self, t):
        self.threads[t.thread_num] = t

    def cmd_list(self):
        print "API Threads:"
        for t in self.threads.values():
            print str(t)

    def cmd_kill(self, n):
        self.threads[n].kill()

    def test(self):
        api = self.api
        v = api.get_vehicles()[0]
        print "Mode: %s" % v.mode
        print "Location: %s" % v.location
        print "Attitude: %s" % v.attitude
        print "GPS: %s" % v.gps_0
        print "Param: %s" % v.parameters['THR_MAX']
        cmds = v.commands
        cmds.download()
        cmds.wait_valid()
        print "Home WP: %s" % cmds[0]
        v.mode = VehicleMode("AUTO")
        v.flush()

    def get_connection(self):
        return self.api

    def cmd_api(self, args):
        if len(args) < 1:
            print("usage: api <list|start|stop> [filename or threadnum]")
            return

        if args[0] == "test":
            APIThread(self, self.test, "Test function")
        elif args[0] == "list":
            self.cmd_list()
        elif args[0] == "stop":
            if len(args) > 2:
                print("usage: api stop [thread-num]")
                return
            elif len(args) > 1:
                self.cmd_kill(int(args[1]))
            elif len(self.threads) > 1:
                # Just kill the youngest
                self.cmd_kill(max(self.threads.keys))
        elif args[0] == "start":
            if len(args) != 2:
                print("usage: api load <filename>")
                return
            g = { "local_connect" : self.get_connection }
            APIThread(self, lambda: execfile(args[1], g), args[1])

def init(mpstate):
    '''initialise module'''
    return APIModule(mpstate)
