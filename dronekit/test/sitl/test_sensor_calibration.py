from pymavlink import mavutil

from dronekit import connect
from dronekit.test import with_sitl

from dronekit.test.sitl import assert_command_ack


@with_sitl
def test_gyro_calibration(connpath):
    """Request gyroscope calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_gyro()

    vehicle.close()


@with_sitl
def test_magnetometer_calibration(connpath):
    """Request magnetometer calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_UNSUPPORTED,  # TODO: change when APM is upgraded
    ):
        vehicle.send_calibrate_magnetometer()

    vehicle.close()


@with_sitl
def test_simple_accelerometer_calibration(connpath):
    """Request simple accelerometer calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_FAILED,
    ):
        vehicle.send_calibrate_accelerometer(simple=True)

    vehicle.close()


@with_sitl
def test_accelerometer_calibration(connpath):
    """Request accelerometer calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    # The calibration is expected to fail because in the SITL we don't tilt the Vehicle.
    # We just check that the command isn't denied or unsupported.
    with assert_command_ack(
        vehicle,
        mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
        timeout=30,
        ack_result=mavutil.mavlink.MAV_RESULT_FAILED,
    ):
        vehicle.send_calibrate_accelerometer(simple=False)

    vehicle.close()


@with_sitl
def test_board_level_calibration(connpath):
    """Request board level calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_vehicle_level()

    vehicle.close()


@with_sitl
def test_barometer_calibration(connpath):
    """Request barometer calibration, and check for the COMMAND_ACK."""

    vehicle = connect(connpath, wait_ready=True)

    with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
        vehicle.send_calibrate_barometer()

    vehicle.close()
