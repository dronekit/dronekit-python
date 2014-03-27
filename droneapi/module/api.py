from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module
from droneapi.lib.DroneApi import APIConnection, Vehicle, VehicleMode

class MPVehicle(Vehicle):
    def __init__(self, module):
        self.__module = module

    def __mavlink_packet(self, m):
        pass

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
    # Operations to support the standard API
    #

    @property
    def mode(self):
        return VehicleMode(self.__module.status.flightmode)
    
    @mode.setter
    def mode(self, v):
        self.__master.set_mode(self.__mode_mapping[v.name])
            
class MPAPIConnection(APIConnection):
    """
    A small private version of the APIConnection class
    
    In Mavproxy you probably just want to call get_vehicles
    """
    def __init__(self, module):
        self.vehicle = MPVehicle(module)

    def get_vehicles(self, query = None):
        return [ self.vehicle ]

    def __mavlink_packet(self, m):
        self.vehicle.__mavlink_packet(m)
        
class APIModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(APIModule, self).__init__(mpstate, "api")
        self.add_command('api', self.cmd_api, "API commands")
        self.api = MPAPIConnection(self)
        print("DroneAPI loaded")

    def mavlink_packet(self, m):
        self.api.__mavlink_packet(m)

    def cmd_api(self, args):
        print "Running test... (FIXME - add python script loading instead)"
        api = self.api
        v = api.get_vehicles()[0]
        print "Old mode: %s" % v.mode
        v.mode = VehicleMode("AUTO")
        v.flush()

def init(mpstate):
    '''initialise module'''
    return APIModule(mpstate)
