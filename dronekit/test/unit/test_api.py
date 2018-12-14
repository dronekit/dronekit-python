from dronekit import VehicleMode
from nose.tools import assert_equals, assert_not_equals


def test_vehicle_mode_eq():
    assert_equals(VehicleMode('GUIDED'), VehicleMode('GUIDED'))


def test_vehicle_mode_neq():
    assert_not_equals(VehicleMode('AUTO'), VehicleMode('GUIDED'))
