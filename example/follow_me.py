import gps
import socket
import time
from droneapi.lib import VehicleMode, Location

def followme():
    """
    followme - A DroneAPI example

    This is a somewhat more 'meaty' example on how to use the DroneAPI.  It uses the
    python gps package to read positions from the GPS attached to your laptop an
    every two seconds it sends a new goto command to the vehicle.

    To use this example:
    * Run mavproxy.py with the correct options to connect to your vehicle
    * module load api
    * api start <path-to-follow_me.py>

    When you want to stop follow-me, either change vehicle modes from your RC
    transmitter or type "api stop".
    """
    try:
        # First get an instance of the API endpoint (the connect via web case will be similar)
        api = local_connect()

        # Now get our vehicle (we assume the user is trying to control the virst vehicle attached to the GCS)
        v = api.get_vehicles()[0]

        # Don't let the user try to fly while the board is still boogint
        if v.mode.name == "INITIALISING":
            print "Vehicle still booting, try again later"
            return

        cmds = v.commands
        is_guided = False  # Have we sent at least one destination point?

        # Use the python gps package to access the laptop GPS
        gpsd = gps.gps(mode=gps.WATCH_ENABLE)

        while not api.exit:
            # This is necessary to read the GPS state from the laptop
            gpsd.next()

            if is_guided and v.mode.name != "GUIDED":
                print "User has changed flight modes - aborting follow-me"
                break

            # Once we have a valid location (see gpsd documentation) we can start moving our vehicle around
            if (gpsd.valid & gps.LATLON_SET) != 0:
                altitude = 30  # in meters
                dest = Location(gpsd.fix.latitude, gpsd.fix.longitude, altitude, is_relative=True)
                print "Going to: %s" % dest

                # A better implementation would only send new waypoints if the position had changed significantly
                cmds.goto(dest)
                is_guided = True
                v.flush()

                # Send a new target every two seconds
                # For a complete implementation of follow me you'd want adjust this delay
                time.sleep(2)
    except socket.error:
        print "Error: gpsd service does not seem to be running, plug in USB GPS or run run-fake-gps.sh"

followme()

