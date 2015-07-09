from nose.tools import assert_raises
from droneapi.lib.WebClient import *
import logging


def setup_module():
    global log
    log = logging.getLogger('WebIntegrationTest')


def teardown_module():
    pass


def test_login_info():
    log.debug('Running web test')
    logging.basicConfig(level=logging.DEBUG)

    def __handleRxMavlink(msg):
        log.debug("MavRx: %s" % msg)

    user = LoginInfo()
    user.loginName = "test-bob-py"
    user.password = "fishpy"
    user.email = "kevinh+pytest2@geeksville.com"
    user.vehicleId = 'a8098c1a-f86e-11da-bd1a-00112444be1e'  # FIXME - store in prefs

    web_client = WebClient(user)
    web_client.connect(__handleRxMavlink)
