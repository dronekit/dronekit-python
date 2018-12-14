import time
from dronekit import connect, VehicleMode
from dronekit.test import with_sitl, wait_for
from nose.tools import assert_equals, assert_not_equals


@with_sitl
def test_timeout(connpath):
    vehicle = connect(connpath, wait_ready=True)

    # NOTE these are *very inappropriate settings*
    # to make on a real vehicle. They are leveraged
    # exclusively for simulation. Take heed!!!
    vehicle.parameters['FS_GCS_ENABLE'] = 0
    vehicle.parameters['FS_EKF_THRESH'] = 100

    def arm_and_takeoff(aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        # Don't let the user try to fly autopilot is booting
        wait_for(lambda: vehicle.is_armable, 60)
        assert_equals(vehicle.is_armable, True)

        # Copter should arm in GUIDED mode
        vehicle.mode = VehicleMode("GUIDED")
        wait_for(lambda: vehicle.mode.name == 'GUIDED', 60)
        assert_equals(vehicle.mode.name, 'GUIDED')

        # Arm copter.
        vehicle.armed = True
        wait_for(lambda: vehicle.armed, 60)
        assert_equals(vehicle.armed, True)

        # Take off to target altitude
        vehicle.simple_takeoff(aTargetAltitude)

        # Wait until the vehicle reaches a safe height before
        # processing the goto (otherwise the command after
        # Vehicle.simple_takeoff will execute immediately).
        while True:
            # print " Altitude: ", vehicle.location.alt
            # Test for altitude just below target, in case of undershoot.
            if vehicle.location.global_frame.alt >= aTargetAltitude * 0.95:
                # print "Reached target altitude"
                break

            assert_equals(vehicle.mode.name, 'GUIDED')
            time.sleep(1)

    arm_and_takeoff(10)
    vehicle.wait_ready('location.local_frame', timeout=60)

    # .north, .east, and .down are initialized to None.
    # Any other value suggests that a LOCAL_POSITION_NED was received and parsed.
    assert_not_equals(vehicle.location.local_frame.north, None)
    assert_not_equals(vehicle.location.local_frame.east, None)
    assert_not_equals(vehicle.location.local_frame.down, None)

    # global_frame
    assert_not_equals(vehicle.location.global_frame.lat, None)
    assert_not_equals(vehicle.location.global_frame.lon, None)
    assert_not_equals(vehicle.location.global_frame.alt, None)
    assert_equals(type(vehicle.location.global_frame.lat), float)
    assert_equals(type(vehicle.location.global_frame.lon), float)
    assert_equals(type(vehicle.location.global_frame.alt), float)

    vehicle.close()


@with_sitl
def test_location_notify(connpath):
    vehicle = connect(connpath)

    ret = {'success': False}

    @vehicle.location.on_attribute('global_frame')
    def callback(*args):
        assert_not_equals(args[2].alt, 0)
        ret['success'] = True

    wait_for(lambda: ret['success'], 30)

    assert ret['success'], 'Expected location object to emit notifications.'

    vehicle.close()
