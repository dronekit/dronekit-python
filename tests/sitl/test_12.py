from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import sys
import os

def current_milli_time():
    return int(round(time.time() * 1000))

def test_timeout(local_connect):
    v = local_connect().get_vehicles()[0]

    print "Read vehicle param 'THR_MIN': %s" % v.parameters['THR_MIN']

    print "Write vehicle param 'THR_MIN' : 50"
    start = current_milli_time()
    v.parameters['THR_MIN']=50
    end = current_milli_time()
    
    print "Read new value of param 'THR_MIN': %s" % v.parameters['THR_MIN']

    # TODO
    # assert end - start < 1000, 'time to set parameter was %s, over 1s' % (end - start,)
