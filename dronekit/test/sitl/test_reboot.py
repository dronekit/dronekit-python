from nose.tools import assert_equal

from dronekit import connect
from dronekit.test import with_sitl
import time


@with_sitl
def test_reboot(connpath):
    """Tries to reboot the vehicle, and checks that the autopilot ACKs the command."""

    vehicle = connect(connpath, wait_ready=True)

    reboot_acks = []

    def on_ack(self, name, message):
        if message.command == 246:  # reboot/shutdown
            reboot_acks.append(message)

    vehicle.add_message_listener('COMMAND_ACK', on_ack)
    vehicle.reboot()
    time.sleep(0.5)
    vehicle.remove_message_listener('COMMAND_ACK', on_ack)

    assert_equal(1, len(reboot_acks))  # one and only one ACK
    assert_equal(246, reboot_acks[0].command)  # for the correct command
    assert_equal(0, reboot_acks[0].result)  # the result must be successful

    vehicle.close()
