import unittest
from droneapi.lib.WebClient import *
import logging

class WebIntegrationTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger('WebIntegrationTest')
        super(WebIntegrationTest, self).__init__(*args, **kwargs)

    def setUp(self):
        """Create simple data set with headers"""
        pass

    def tearDown(self):
        """Teardown."""
        pass

    def test_login_info(self):
        self.log.debug('Running web test')
        logging.basicConfig(level=logging.DEBUG)

        def __handleRxMavlink(msg):
            self.log.debug("MavRx: %s" % msg)

        user = LoginInfo()
        user.loginName = "test-bob-py"
        user.password = "fishpy"
        user.email = "kevinh+pytest2@geeksville.com"
        user.vehicleId = 'a8098c1a-f86e-11da-bd1a-00112444be1e' # FIXME - store in prefs

        web_client = WebClient(user)
        web_client.connect(__handleRxMavlink)


if __name__ == '__main__':
    unittest.main()
