import mock
from mock import MagicMock
import droneapi
from droneapi.module.api import APIModule
from nose.tools import assert_equals

def test_mode():
    api = APIModule(MagicMock())
    res = api.get_connection()
    assert_equals(len(res.get_vehicles()), 1)
