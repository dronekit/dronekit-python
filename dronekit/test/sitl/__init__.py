import time
from contextlib import contextmanager
from nose.tools import assert_equal
from pymavlink import mavutil


@contextmanager
def assert_command_ack(
    vehicle,
    command_type,
    ack_result=mavutil.mavlink.MAV_RESULT_ACCEPTED,
    timeout=10
):
    """Context manager to assert that:

    1) exactly one COMMAND_ACK is received from a Vehicle;
    2) for a specific command type;
    3) with the given result;
    4) within a timeout (in seconds).

    For example:

    .. code-block:: python

        with assert_command_ack(vehicle, mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION, timeout=30):
            vehicle.calibrate_gyro()

    """

    acks = []

    def on_ack(self, name, message):
        if message.command == command_type:
            acks.append(message)

    vehicle.add_message_listener('COMMAND_ACK', on_ack)

    yield

    start_time = time.time()
    while not acks and time.time() - start_time < timeout:
        time.sleep(0.1)
    vehicle.remove_message_listener('COMMAND_ACK', on_ack)

    assert_equal(1, len(acks))  # one and only one ACK
    assert_equal(command_type, acks[0].command)  # for the correct command
    assert_equal(ack_result, acks[0].result)  # the result must be successful
