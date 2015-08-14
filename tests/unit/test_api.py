import mock
from mock import MagicMock
from nose.tools import eq_, assert_not_equal
import droneapi
from droneapi.module.api import APIModule
from droneapi.lib import VehicleMode
from nose.tools import assert_equals

def test_get_vehicles():
    api = APIModule(MagicMock())
    res = api.get_connection()
    eq_(len(res.get_vehicles()), 1)

def test_vehicle_mode_eq():
    eq_(VehicleMode('GUIDED'), VehicleMode('GUIDED'))

def test_vehicle_mode_neq():
    assert_not_equal(VehicleMode('AUTO'), VehicleMode('GUIDED'))
