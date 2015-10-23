import mock
from mock import MagicMock
import dronekit
from dronekit.lib import VehicleMode
from dronekit import FakeAPI
from nose.tools import assert_equals, assert_not_equals

def test_mode():
    api = FakeAPI(MagicMock())
    assert_equals(len(api.get_vehicles()), 1)

def test_vehicle_mode_eq():
    assert_equals(VehicleMode('GUIDED'), VehicleMode('GUIDED'))

def test_vehicle_mode_neq():
    assert_not_equals(VehicleMode('AUTO'), VehicleMode('GUIDED'))
