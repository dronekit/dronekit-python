import os
from nose.tools import assert_raises
from dronekit.cloud.CloudClient import *


def setup_module():
    global api
    api_key = os.environ['DRONEAPI_KEY']
    api = CloudClient(api_key)


def teardown_module():
    pass


def test_unhandled_endpoint():
    assert_raises(CloudError, api.bogus)


def test_mission_endpoint():
    api.mission()


def test_mission_static_map():
    api.mission_staticMap()


def test_mission_by_id_endpoint():
    api.mission_(1141)


def test_mission_by_id_analysis_endpoint():
    api.mission_analysis(1141)


def test_mission_by_id_geo_endpoint():
    api.mission_geo(1141)


def test_mission_by_id_messages_endpoint():
    api.mission_messages(1141)


def test_mission_by_id_parameters_endpoint():
    api.mission_parameters(1141)


def test_mission_by_id_dseries_endpoint():
    api.mission_dseries(1141)


def test_vehicle_endpoint():
    api.vehicle()


def test_vehicle_by_id_endpoint():
    api.vehicle_(218)


def test_user_endpoint():
    api.user()


def test_user_by_login_endpoint():
    api.user('mrpollo')
