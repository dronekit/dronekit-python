"""
drone_delivery.py: 

A CherryPy based web application that displays a mapbox map to let you view the current vehicle position and send the vehicle commands to fly to a particular latitude and longitude.

Full documentation is provided at http://python.dronekit.io/examples/drone_delivery.html
"""
import os, os.path
import simplejson

from pymavlink import mavutil
import dronekit.lib
from dronekit import connect
from dronekit.lib import VehicleMode, LocationGlobal

import cherrypy
from cherrypy.process import wspbus, plugins
from jinja2 import Environment, FileSystemLoader


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()



local_path=os.path.dirname(os.path.abspath(__file__))
print "local path: %s" % local_path



cherrypy_conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': local_path
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './html/assets'
    }
}

class Drone(object):
    def __init__(self, home_coords, server_enabled=True):
        # Connect to the Vehicle
        print 'Connecting to vehicle on: %s' % args.connect
        self.vehicle = connect(args.connect, wait_ready=True)
        print "connected ..."
        self.gps_lock = False
        self.altitude = 30.0
        self.commands = self.vehicle.commands
        self.current_coords = []
        self.home_coords = home_coords
        self.webserver_enabled = server_enabled
        self._log("DroneDelivery Start")

        # Register observers
        self.vehicle.add_attribute_listener('armed', self.armed_callback)
        self.vehicle.add_attribute_listener('location', self.location_callback)
        #self.vehicle.add_attribute_listener('mode', self.mode_callback)
        self.vehicle.add_attribute_listener('gps_0', self.gps_callback)

        self._log("Waiting for GPS Lock")

    def takeoff(self):
        self._log("Taking off")
        self.commands.takeoff(30.0)

    def arm(self):
        self._log("Arming")
        self.vehicle.armed = True

    def run(self):
        self._log('Running initial boot sequence')
        self.arm()
        self.takeoff()
        self.change_mode('GUIDED')

        if self.webserver_enabled is True:
            self._run_server()

    def _run_server(self):
        # Start web server if enabled
        cherrypy.tree.mount(DroneDelivery(self), '/', config=cherrypy_conf)

        cherrypy.config.update({
            'server.socket_port': 8080,
            'server.socket_host': '0.0.0.0',
            'log.screen': None
         })

        cherrypy.engine.start()

    def change_mode(self, mode):
        self._log("Mode: {0}".format(mode))
        self.vehicle.mode = VehicleMode(mode)


    def goto(self, location, relative=None):
        self._log("Goto: {0}, {1}".format(location, self.altitude))

        self.commands.goto(
            Location(
                float(location[0]), float(location[1]),
                float(self.altitude),
                is_relative=relative
            )
        )

    def get_location(self):
        return [self.current_location.lat, self.current_location.lon]

    def location_callback(self, location):
        location = self.vehicle.location.global_frame

        if location.alt is not None:
            self.altitude = location.alt

        self.current_location = location

    def armed_callback(self, armed):
        self._log("DroneDelivery Armed Callback")
        self.vehicle.remove_message_listener('armed', self.armed_callback)

    def mode_callback(self, mode):
        self._log("Mode: {0}".format(self.vehicle.mode))

    def gps_callback(self, gps):
        self._log("GPS: {0}".format(self.vehicle.gps_0))
        if self.gps_lock is False:
            self.gps_lock = True
            self.vehicle.remove_message_listener('gps_0', self.gps_callback)
            self.run()

    def _log(self, message):
        print "[DEBUG]: {0}".format(message)

class Templates:
    def __init__(self, home_coords):
        self.home_coords = home_coords
        self.options = self.get_options()
        self.environment = Environment(loader=FileSystemLoader( local_path + '/html'))

    def get_options(self):
        return {
                'width': 670,
                'height': 470,
                'zoom': 13,
                'format': 'png',
                'access_token': 'pk.eyJ1IjoibXJwb2xsbyIsImEiOiJtUG0tRk9BIn0.AqAiefUV9fFYRo-w0jFR1Q',
                'mapid': 'mrpollo.kfbnjbl0',
                'home_coords': self.home_coords,
                'menu': [
                    {'name': 'Home', 'location': '/'},
                    {'name': 'Track', 'location': '/track'},
                    {'name': 'Command', 'location': '/command'}
                    ],
                'current_url': '/',
                'json': ''
                }

    def index(self):
        self.options = self.get_options()
        self.options['current_url'] = '/'
        return self.get_template('index')

    def track(self, current_coords):
        self.options = self.get_options()
        self.options['current_url'] = '/track'
        self.options['current_coords'] = current_coords
        self.options['json'] = simplejson.dumps(self.options)
        return self.get_template('track')

    def command(self, current_coords):
        self.options = self.get_options()
        self.options['current_url'] = '/command'
        self.options['current_coords'] = current_coords
        return self.get_template('command')

    def get_template(self, file_name):
        template = self.environment.get_template( file_name + '.html')
        return template.render(options=self.options)

class DroneDelivery(object):
    def __init__(self, drone):
        self.drone = drone
        self.templates = Templates(self.drone.home_coords)

    @cherrypy.expose
    def index(self):
        return self.templates.index()

    @cherrypy.expose
    def command(self):
        return self.templates.command(self.drone.get_location())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vehicle(self):
        return dict(position=self.drone.get_location())

    @cherrypy.expose
    def track(self, lat=None, lon=None):
        # Process POST request from Command
        # Sending MAVLink packet with goto instructions
        if(lat is not None and lon is not None):
            self.drone.goto([lat, lon], True)

        return self.templates.track(self.drone.get_location())

Drone([32.5738, -117.0068])
cherrypy.engine.block()

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()
print("Completed")
