

# Simple Goto Demo

This little demonstration just tells the vehicle to fly to a couple of different locations in the world.  You can edit the code to pick a latitude and longitude close to your position.

## Running the example

Once Mavproxy is running and the API is loaded, you can run this small example by typing "api start simple_goto.py."

It will tell your vehicle to start flying to a particular latitude and longitude stored in the file (though for safety the take-off command is not included - you must manually tell vehicle to fly).  On the mavproxy console you should see:

<pre>
STABILIZE> api start simple_goto.py
STABILIZE> Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
GUIDED> Mode GUIDED
APIThread-0 exiting...
Got MAVLink msg: MISSION_ACK {target_system : 255, target_component : 0, type : 0}
</pre>

## How does it work?

The key code in this demo is the following:

<pre>
vehicle.mode    = VehicleMode("GUIDED")
origin          = Location(-34.364114, 149.166022, 30, is_relative=True)

commands.goto(origin)
vehicle.flush()
</pre>

It tells the vehicle to fly to a specified lat/long and hover at that location (30 meters in the air).  is_relative=True is the default and is recommended - it means that the altitude (30 meters) is _relative_ to the vehicle home location.  If you had set is_relative to false, it would have told the vehicle to fly to a specified mean-sea-level which is probably not what you want unless you are next to an ocean.

