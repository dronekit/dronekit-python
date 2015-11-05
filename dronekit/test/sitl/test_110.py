import time
import sys
import os
from dronekit import connect, VehicleMode
from dronekit.test import with_sitl
from nose.tools import assert_equals

@with_sitl
def test_110(connpath):
    v = connect(connpath, wait_ready=True)

    # NOTE these are *very inappropriate settings*
    # to make on a real vehicle. They are leveraged
    # exclusively for simulation. Take heed!!!
    v.parameters['ARMING_CHECK'] = 0
    v.parameters['FS_THR_ENABLE'] = 0
    v.parameters['FS_GCS_ENABLE'] = 0
    v.parameters['EKF_CHECK_THRESH'] = 0
    
    # Change the vehicle into STABILIZE mode
    v.mode = VehicleMode("STABILIZE")

    # NOTE wait crudely for ACK on mode update
    time.sleep(3)

    # Define example callback for mode
    def armed_callback(vehicle, attribute):
        armed_callback.called += 1
    armed_callback.called = 0

    # When the same (event, callback) pair is passed to on_attribute,
    # only one instance of the observer callback should be added.
    v.on_attribute('armed', armed_callback)
    v.on_attribute('armed', armed_callback)
    v.on_attribute('armed', armed_callback)
    v.on_attribute('armed', armed_callback)
    v.on_attribute('armed', armed_callback)

    # Disarm and see update.
    v.armed = False
    # Wait for ACK.
    time.sleep(3)

    # Ensure the callback was called.
    assert armed_callback.called > 0, "Callback should have been called."

    # Rmove all listeners. The first call should remove all listeners
    # we've added; the second call should be ignored and not throw.
    # NOTE: We test if armed_callback were treating adding each additional callback
    # and remove_attribute_listener were removing them one at a time; in this
    # case, there would be three callbacks still attached.
    v.remove_attribute_listener('armed', armed_callback)
    v.remove_attribute_listener('armed', armed_callback)
    callcount = armed_callback.called

    # Re-arm and see update.
    v.armed = True
    # Wait for ack
    time.sleep(3)

    # Ensure the callback was called zero times.
    assert_equals(armed_callback.called, callcount, "Callback should not have been called once removed.")

    v.close()
