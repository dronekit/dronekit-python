import unittest
import os
from droneapi.lib.CloudClient import *

class CloudClientTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        api_key = os.environ['DRONEAPI_KEY']
        self.api = CloudClient(api_key)
        super(CloudClientTest, self).__init__(*args, **kwargs)

    def setUp(self):
        """Create simple data set with headers"""
        pass

    def tearDown(self):
        """Teardown."""
        pass

    def test_unhandled_endpoint(self):
        self.assertRaises(CloudError, self.api.bogus)

    def test_mission_endpoint(self):
        self.api.mission()

    def test_mission_static_map(self):
        self.api.mission_staticMap()

    def test_mission_by_id_endpoint(self):
        self.api.mission_(1141)

    def test_mission_by_id_analysis_endpoint(self):
        self.api.mission_analysis(1141)

    def test_mission_by_id_geo_endpoint(self):
        self.api.mission_geo(1141)

    def test_mission_by_id_messages_endpoint(self):
        self.api.mission_messages(1141)

    def test_mission_by_id_parameters_endpoint(self):
        self.api.mission_parameters(1141)

    def test_mission_by_id_dseries_endpoint(self):
        self.api.mission_dseries(1141)

    def test_vehicle_endpoint(self):
        self.api.vehicle()

    def test_vehicle_by_id_endpoint(self):
        self.api.vehicle_(218)

    def test_user_endpoint(self):
        self.api.user()

    def test_user_by_login_endpoint(self):
        self.api.user('mrpollo')

if __name__ == '__main__':
    unittest.main()
