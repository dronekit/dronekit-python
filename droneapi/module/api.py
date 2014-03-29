from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module
from droneapi.lib import APIConnection, Vehicle, VehicleMode, Location,\
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
        self.__module.master.waypoint_request_list_send()
        # BIG FIXME - wait for full wpt download before allowing any of the accessors to work

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
        self._waypoints = MPCommandSequence(module)

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
         
class MPAPIConnection(APIConnection):
    """
    A small private version of the APIConnection class
    
    In Mavproxy you probably just want to call get_vehicles
    """
    def __init__(self, module):
        self.__vehicle = MPVehicle(module)

    def get_vehicles(self, query = None):
        return [ self.__vehicle ]
        
class APIModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(APIModule, self).__init__(mpstate, "api")
        self.add_command('api', self.cmd_api, "API commands", [ "<test>", "<load> (FILENAME)" ])
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
        self.fix_type = None # FIXME support multiple GPSs per vehicle - possibly by using componentId
        print("DroneAPI loaded")

    def __on_change(self, *args):
        for a in args:
            self.vehicle.notify_observers(a)
            
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
    
    def test(self):
        api = self.api
        v = api.get_vehicles()[0]
        print "Mode: %s" % v.mode
        print "Location: %s" % v.location
        print "Attitude: %s" % v.attitude
        print "GPS: %s" % v.gps_0
        print "Param: %s" % v.parameters['THR_MAX']
        print "Home WP: %s" % v.commands[0]
        v.mode = VehicleMode("AUTO")
        v.flush()
    
    def get_connection(self):
        return self.api
    
    def cmd_api(self, args):
        if len(args) < 1:
            print("usage: api <test|load> <filename>")
            return
    
        if args[0] == "test":
            self.test()
        elif args[0] == "load":
            if len(args) != 2:
                print("usage: api load <filename>")
                return
            globals = { "local_connect" : self.get_connection }
            execfile(args[1], globals)

def init(mpstate):
    '''initialise module'''
    return APIModule(mpstate)
