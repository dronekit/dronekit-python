from droneapi.lib import VehicleMode
from pymavlink import mavutil
import time
import sys
import os

def test_110(local_connect):
    api = local_connect()
    v = api.get_vehicles()[0]
    
    # Change the vehicle into STABILIZE mode
    v.mode = VehicleMode("STABILIZE")

    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Define example callback for mode
    allow_callback = True
    bad_call = [False]
    def armed_callback(attribute):
        if not allow_callback:
            bad_call[0] = True

    # Only one of the same observer fn should be added.
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    allow_callback = True

    # Disarm and see update.
    v.armed = False
    v.flush()

    time.sleep(3)

    # Rmove (all) observers.
    v.remove_attribute_observer('armed', armed_callback)
    v.remove_attribute_observer('armed', armed_callback)
    allow_callback = False

    # Re-arm and see update.
    v.armed = True
    v.flush()

    time.sleep(3)

    # Make sure no bad calls happened.
    assert not bad_call[0], "Callback should not have been called once removed."
