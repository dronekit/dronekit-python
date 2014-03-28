from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module
from droneapi.lib.DroneApi import APIConnection, Vehicle, VehicleMode, Location,\
    Attitude

"""
fixme make params work
fixme do follow me example
fixme make mission work
"""

class MPVehicle(Vehicle):
    def __init__(self, module):
        self.__module = module

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
        self.add_command('api', self.cmd_api, "API commands")
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
        print("DroneAPI loaded")

    def __on_change(self, **args):
        for a in args:
            self.vehicle.notify_observers(a)
            
    def mavlink_packet(self, m):
        if m.get_type() == 'GPS_RAW':
            (self.lat, self.lon) = (m.lat, m.lon)
            self.__on_change('location')
        elif m.get_type() == 'GPS_RAW_INT':
            (self.lat, self.lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            self.__on_change('location')
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
            
    def cmd_api(self, args):
        print "Running test... (FIXME - add python script loading instead)"
        api = self.api
        v = api.get_vehicles()[0]
        print "Mode: %s" % v.mode
        print "Location: %s" % v.location
        print "Attitude: %s" % v.attitude
        v.mode = VehicleMode("AUTO")
        v.flush()

def init(mpstate):
    '''initialise module'''
    return APIModule(mpstate)
