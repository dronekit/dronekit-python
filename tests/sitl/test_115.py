from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import sys
import os

def test_115(local_connect):
    api = local_connect()
    v = api.get_vehicles()[0]

    # Dummy callback
    def noop(*args):
        pass

    # Set the callback.
    v.set_mavlink_callback(noop)
    
    # Change the vehicle into STABILIZE mode
    v.mode = VehicleMode("STABILIZE")

    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Unset the callback.
    v.set_mavlink_callback(None)

    # Disarm should not throw errors.
    v.armed = False
    v.flush()

    time.sleep(3)

    # Re-arm should not throw errors.
    v.armed = True
    v.flush()

    time.sleep(3)
