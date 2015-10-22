"""
flight_replay.py: 

This example requests a past flight from Droneshare, and then 'replays' 
the flight by sending waypoints to a vehicle.

Full documentation is provided at http://python.dronekit.io/examples/flight_replay.html
"""

from dronekit import connect
from dronekit.lib import Command
from pymavlink import mavutil
import json, urllib, math

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Get a flight from droneshare and send as waypoints to a vehicle. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
parser.add_argument('--mission_id', default='101',
                   help="DroneShare Mission ID to replay. Default is '101'")                   
parser.add_argument('--api_server', default='https://api.3drobotics.com',
                   help="API Server. Default is Droneshare API (https://api.3drobotics.com)")
parser.add_argument('--api_key', default='89b511b1.d884d1cb57306e63925fcc07d032f2af',
                   help="API Server Key (default should be fine!)")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, await_params=True)



def _decode_list(data):
    """A utility function for decoding JSON strings from unicode"""
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    """A utility function for decoding JSON strings from Unicode"""
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def download_messages(mission_id, max_freq = 1.0):
    """Download a public mission from droneshare (as JSON)"""
    message_url="%s/api/v1/mission/%s/messages.json?max_freq=%s&api_key=%s" % (args.api_server, mission_id, max_freq, args.api_key)
    f = urllib.urlopen(message_url)
    j = json.load(f, object_hook=_decode_dict)
    f.close()
    return j

def replay_mission(payload):
    """Given mission JSON, set a series of wpts approximating the previous flight"""
    # Pull out just the global position msgs
    try:
        messages = payload['messages']
    except:
        print "Exception: payload from site is: %s" % payload
        sys.exit()
    messages = filter(lambda obj: obj['typ'] == 'MAVLINK_MSG_ID_GLOBAL_POSITION_INT', messages)
    messages = map(lambda obj: obj['fld'], messages)

    # Shrink the # of pts to be lower than the max # of wpts allowed by vehicle
    num_points = len(messages)
    max_points = 99
    if num_points > max_points:
        step = int(math.ceil((float(num_points) / max_points)))
        shorter = [messages[i] for i in xrange(0, num_points, step)]
        messages = shorter

    print "Generating %s waypoints from replay..." % len(messages)
    cmds = vehicle.commands
    cmds.clear()
    vehicle.flush()
    for i in xrange(0, len(messages)):
        pt = messages[i]
        lat = pt['lat']
        lon = pt['lon']
        # To prevent accidents we don't trust the altitude in the original flight, instead
        # we just put in a conservative cruising altitude.
        altitude = 30.0 # pt['alt']
        cmd = Command( 0,
                       0,
                       0,
                       mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                       mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                       0, 0, 0, 0, 0, 0,
                       lat, lon, altitude)
        cmds.add(cmd)
    vehicle.flush()


# Now download the vehicle waypoints
cmds = vehicle.commands
cmds.wait_valid()
mission_id = int(args.mission_id)
max_freq = 0.1
json = download_messages(mission_id, max_freq)
print "JSON downloaded..."
replay_mission(json)


#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()
print("Completed...")
