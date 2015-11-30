# Changelog

## Version 2.0.2 (2015-11-30)

### Bug Fixes:

* Updates `requests` dependency to work >=2.5.0


## Version 2.0.0 (2015-11-23)

### New Features:

* Renamed library and package from DroneAPI to DroneKit on pip
* DroneKit Python is now a standalone library and no longer requires use of MAVProxy
* Connect multiple vehicles in one script by creating separate vehicle instances
* Removed NumPy, ProtoBuf as dependencies
* Add MAVLink message listeners using `add_message_listener` methods
* Added `on_attribute` and `on_message` function decorator shorthands
* Added `mount_status`, `system_status`, `ekf_ok`, `is_armable`, `heading`
* Made settable `groundspeed`, `airspeed`
* Moved `dronekit.lib` entries to root package `dronekit`
* Added `parameters.set` and `parameters.get` for fine-tuned parameter access
* `parameters` now observable and iterable (#442)
* Added `last_heartbeat` attribute, updated every event loop with time since last heartbeat (#451)
* Await attributes through `wait_ready` method and `connect` method parameter
* Adds subclassable Vehicle class, used by `vehicle_class` parameter in `connect`

### Updated Features:

* local_connect renamed to connect(), accepting a connection path, link configuration, and timeout settings
* Removed `.set_mavrx_callback`. Use `vehicle.on_message('*', obj)` methods
* Renamed `add_attribute_observer` methods to `add_attribute_listener`, etc. (#420)
* Renamed `wait_init` and `wait_valid` to `wait_ready`
* Split `home_location` is a separate attribute from `commands` waypoint array
* Moved RC channels into `.channels` object (#427)
* Split location information into `local_frame`, `global_frame`, and `global_relative_frame` (and removed `is_relative`) (#445)
* Renamed `flush` to `commands.upload`, as it only impacts waypoints (#276)
* `commands.goto` and `commands.takeoff` renamed to `simple_goto` and `simple_takeoff`

### Bug Fixes:

* `armed` and `mode` attributes updated constantly (#60, #446)
* Parameter setting times out (#12)
* `battery` access can throw exception (#298)
* Vehicle.location reports incorrect is_relative value for Copter (#130)
* Excess arming message when already armed
