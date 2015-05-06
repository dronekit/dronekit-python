#
# This is an example of talking to Droneshare to receive a past flight, and then 'replaying' that flight by sending waypoints
# to the vehicle that approximates the stored flight log.
# Usage:
# * mavproxy.py
# * module load api
# * api start flight_replay.py <missionid>
# (Where mission ID is a numeric mission number from a public droneshare flight)
#
from droneapi.lib import Command
from pymavlink import mavutil
import json, urllib, math

api_server = "https://api.3drobotics.com"
api_key = "a8948c11.9e44351f6c0aa7e3e2ff6d00b14a71c5"

# First get an instance of the API endpoint
api = local_connect()
# Get our vehicle - when running with MAVProxy it only knows about one vehicle (for now)
v = api.get_vehicles()[0]


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
    f = urllib.urlopen("%s/api/v1/mission/%s/messages.json?max_freq=%s&api_key=%s" % (api_server, mission_id, max_freq, api_key))
    j = json.load(f, object_hook=_decode_dict)
    f.close()
    return j

def replay_mission(payload):
    """Given mission JSON, set a series of wpts approximating the previous flight"""
    # Pull out just the global position msgs
    messages = payload['messages']
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
    cmds = v.commands
    cmds.clear()
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
    v.flush()

if len(local_arguments) != 1:
    print 'Error: usage "api start flight_replay.py <missionid>"'
else:
    # Now download the vehicle waypoints
    cmds = v.commands
    cmds.wait_valid()

    mission_id = int(local_arguments[0])
    max_freq = 0.1
    json = download_messages(mission_id, max_freq)
    print "JSON downloaded..."
    replay_mission(json)
