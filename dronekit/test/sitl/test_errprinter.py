import logging
import time

from nose.tools import assert_true

from dronekit import connect
from dronekit.test import with_sitl


@with_sitl
def test_115(connpath):
    """Provide a custom status_printer function to the Vehicle and check that
    the autopilot messages are correctly logged.
    """

    logging_check = {'ok': False}

    def errprinter_fn(msg):
        if isinstance(msg, str) and "APM:Copter" in msg:
            logging_check['ok'] = True

    vehicle = connect(connpath, wait_ready=False, status_printer=errprinter_fn)

    i = 5
    while not logging_check['ok'] and i > 0:
        time.sleep(1)
        i -= 1

    assert_true(logging_check['ok'])
    vehicle.close()

    # Cleanup the logger
    autopilotLogger = logging.getLogger('autopilot')
    autopilotLogger.removeHandler(autopilotLogger.handlers[0])
