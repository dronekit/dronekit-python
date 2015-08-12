from droneapi import local_connect
from droneapi.lib import VehicleMode
from droneapi.tools import with_sitl
from pymavlink import mavutil
import time
import sys
import os
from nose.tests import assert_equals

@with_sitl
def test_110(connpath):
    api = local_connect(connpath)
    v = api.get_vehicles()[0]
    
    # Change the vehicle into STABILIZE mode
    v.mode = VehicleMode("STABILIZE")

    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Define example callback for mode
    def armed_callback(attribute):
        armed_callback.called += 1
    armed_callback.called = 0

    # When the same (event, callback) pair is passed to add_attribute_observer,
    # only one instance of the observer callback should be added.
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)
    v.add_attribute_observer('armed', armed_callback)

    # Disarm and see update.
    v.armed = False
    v.flush()
    # Wait for ACK.
    time.sleep(3)

    # Ensure the callback was called.
    assert armed_callback.called > 0, "Callback should have been called."

    # Rmove all observers. The first call should remove all listeners
    # we've added; the second call should be ignored and not throw.
    # NOTE: We test if armed_callback were treating adding each additional callback
    # and remove_attribute_observer were removing them one at a time; in this
    # case, there would be three callbacks still attached.
    v.remove_attribute_observer('armed', armed_callback)
    v.remove_attribute_observer('armed', armed_callback)
    callcount = armed_callback.called

    # Re-arm and see update.
    v.armed = True
    v.flush()
    # Wait for ack
    time.sleep(3)

    # Ensure the callback was called zero times.
    assert_equals(armed_callback.called, callcount, "Callback should not have been called once removed.")
