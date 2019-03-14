# Changelog


## Version 2.9.2 (2019-03-18)

### Improvements
* CI integration improvements
* Python3 compatability
* use logging module
* log statustexts
* documentation improvements
* convenience functions added: wait_for, wait_for_armable, arm, disarm, wait_for_mode, wait_for_alt, wait_simple_takeoff
* play_tune method added
* reboot method added
* send_calibrate_gyro, send_calibrate_magnetometer, send_calibrate_magnetometer, send_calibrate_vehicle_level, send_calibrate_barometer all added
* update gimbal orientation from MOUNT_ORIENTATION
* add a still-waiting callback for connect() to provide debug on where the connection is up to
* several new tests added (including, play_tune, reboot and set_attitude_target)

### Cleanup
* flake8 compliance improvements
* test includes pruned
* examples cleaned up

### Bug Fixes
* ignore GCS heartbeats for the purposes of link up
* many!

## Version 2.9.1 (2017-04-21)

### Improvements
* home locatin notifications
* notify ci status to gitter
* basic python 3 support
* isolated logger function so implementers can override
* rename windows installer

### Cleanup
* removed legacy cloud integrations

### Bug Fixes
* fix missing ** operator for pymavlink compatibility

## Version 2.9.0 (2016-08-29)

### Bug Fixes
* MAVConnection stops threads on exit and close
* PX4 Pro flight modes are now properly supported
* go to test now uses correct `global_relative_frame` alt

### Improvements
* Updated pymavlink dependency to v2 from v1 hoping we don't fall behind
  again.

## Version 2.8.0 (2016-07-15)

### Bug Fixes
* Makes sure we are listening to `HOME_LOCATION` message, befor we
  would only set home location if received by waypoints.

## Version 2.7.0 (2016-06-21)

### Improvements
* Adds udpin-multi support

## Version 2.6.0 (2016-06-17)

### Bug Fixes
* Fixes patched mavutil sendfn

## Version 2.5.0 (2016-05-04)

### Improvements
* Catch and display message and attribute errors, then continue
* Improved takeoff example docs
* Deploy docs on successful merge into master (from CircleCI)
* Drone delivery example, explain port to connect
* MicroCGS example now uses SITL
* Make running examples possible on Vagrant

### Bug Fixes
* Mav type for rover was incorrect
* `_is_mode_available` can now handle unrecognized mode codes
* Fix broken links on companion computer page
* Fix infinite loop on channel test



## Version 2.4.0 (2016-02-29)

### Bug Fixes

* Use monotonic clock for all of the internal timeouts and time
  measurements
* Docs fixes


## Version 2.3.0 (2016-02-26)

### New Features

* PX4 compatibility improvements

### Updated Features

* Documentation fixes
* PIP repository improvements
* Mode-setting API improvements
* ardupilot-solo compatibility fixes



## Version 2.2.0 (2016-02-19)

### Bug Fixes

* Splits outbound messages into its own thread.
* Remove of capabilities request on HEARTBEAT listener
* Check if mode_mapping has items before iteration



## Version 2.1.0 (2016-02-16)


### New Features


* Gimbal control attribute
* Autopilot version attribute
* Autopilot capabilities attribute
* Best Practice guide documentation.
* Performance test example (restructured and docs added)

### Updated Features:

Many documentation fixes:

* Restructured documentation with Develop (Concepts) and Guide (HowTo) sections
* Docs separated out "Connection Strings" section.
* Improved test and contribution sections.
* Updated examples and documentation to use DroneKit-Sitl for simulation ("zero setup examples")
* Debugging docs updated with additional libraries.
* Flight Replay example fetches data from TLOG rather than droneshare
* Drone Delivery example now uses strart location for home address.
* Disabled web tests (not currently supported/used)
* Updated copyright range to include changes in 2016

### Bug Fixes

* Numerous minor docs fixes.
* Harmonise nosetest options across each of the integration platforms
* Fix incorrect property marker for airspeed attribute



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
