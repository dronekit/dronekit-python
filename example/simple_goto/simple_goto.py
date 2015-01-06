import time
from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil

api             = local_connect()
vehicle         = api.get_vehicles()[0]
commands        = vehicle.commands
vehicle.mode    = VehicleMode("GUIDED")
origin          = Location(-34.364114, 149.166022, 30, is_relative=True)

commands.goto(origin)
vehicle.flush()

# sleep 2 seconds so we can see the change in map
time.sleep(2)

destination     = Location(-35.3632610, 149.1652300, 30, is_relative=True)

commands.goto(destination)
vehicle.flush()
