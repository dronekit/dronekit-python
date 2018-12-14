import time
import socket
from dronekit import connect
from dronekit.test import with_sitl
from nose.tools import assert_equals


@with_sitl
def test_timeout(connpath):
    # Connect with timeout of 10s.
    vehicle = connect(connpath, wait_ready=True, heartbeat_timeout=20)

    # Stall input.
    vehicle._handler._accept_input = False

    start = time.time()
    while vehicle._handler._alive and time.time() - start < 30:
        time.sleep(.1)

    assert_equals(vehicle._handler._alive, False)

    vehicle.close()


def test_timeout_empty():
    # Create a dummy server.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 5760))
    s.listen(1)

    try:
        # Connect with timeout of 10s.
        vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True, heartbeat_timeout=20)

        vehicle.close()

        # Should not pass
        assert False
    except:
        pass
