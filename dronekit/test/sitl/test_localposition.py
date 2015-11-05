import time
from dronekit import connect, VehicleMode, LocationGlobal
from dronekit.test import with_sitl
from nose.tools import assert_equals, assert_not_equals

@with_sitl
def test_timeout(connpath):
    vehicle = connect(connpath, wait_ready=True)

    # NOTE these are *very inappropriate settings*
    # to make on a real vehicle. They are leveraged
    # exclusively for simulation. Take heed!!!
    vehicle.parameters['ARMING_CHECK'] = 0
    vehicle.parameters['FS_THR_ENABLE'] = 0
    vehicle.parameters['FS_GCS_ENABLE'] = 0
    vehicle.parameters['EKF_CHECK_THRESH'] = 0

    def arm_and_takeoff(aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """

        # print "Basic pre-arm checks"
        # Don't let the user try to fly autopilot is booting
        if vehicle.mode.name == "INITIALISING":
            # print "Waiting for vehicle to initialise"
            time.sleep(1)
        while vehicle.gps_0.fix_type < 2:
            # print "Waiting for GPS...:", vehicle.gps_0.fix_type
            time.sleep(1)
            
        # print "Arming motors"
        # Copter should arm in GUIDED mode
        vehicle.mode    = VehicleMode("GUIDED")

        i = 60
        while vehicle.mode.name != 'GUIDED' and i > 0:
            # print " Waiting for guided %s seconds..." % (i,)
            time.sleep(1)
            i = i - 1

        vehicle.armed = True

        i = 60
        while not vehicle.armed and vehicle.mode.name == 'GUIDED' and i > 0:
            # print " Waiting for arming %s seconds..." % (i,)
            time.sleep(1)
            i = i - 1

        # Failure will result in arming but immediately landing
        assert vehicle.armed
        assert_equals(vehicle.mode.name, 'GUIDED')

        # print "Taking off!"
        vehicle.commands.takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before
        # processing the goto (otherwise the command after
        # Vehicle.commands.takeoff will execute immediately).
        while True:
            # print " Altitude: ", vehicle.location.alt
            # Test for altitude just below target, in case of undershoot.
            if vehicle.location.global_frame.alt >= aTargetAltitude * 0.95: 
                # print "Reached target altitude"
                break

            assert_equals(vehicle.mode.name, 'GUIDED')
            time.sleep(1)

    arm_and_takeoff(10)
    vehicle.wait_ready('local_position', timeout=60)
    
    # .north, .east, and .down are initialized to None.
    # Any other value suggests that a LOCAL_POSITION_NED was received and parsed.
    assert_not_equals(vehicle.location.local_frame.north, None)
    assert_not_equals(vehicle.location.local_frame.east, None)
    assert_not_equals(vehicle.location.local_frame.down, None)

    vehicle.close()
