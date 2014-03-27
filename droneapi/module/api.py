from pymavlink import mavutil
from MAVProxy.modules.lib import mp_module
from droneapi.lib.DroneApi import APIConnection, Vehicle

class MPVehicle(Vehicle):
    pass
    
class MPAPIConnection(APIConnection):
    def __init__(self):
        self.vehicle = MPVehicle()

    def get_vehicles(self, fixme):
        return [ self.vehicle ]


class APIModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(APIModule, self).__init__(mpstate, "api")
        self.add_command('api', self.cmd_tracker, "API commands")
        print("DroneAPI loaded")
    
    def mavlink_packet(self, m):
        pass

    def cmd_tracker(self, args):
        pass
    
def init(mpstate):
    '''initialise module'''
    return APIModule(mpstate)