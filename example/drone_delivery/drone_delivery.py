import os, os.path
import simplejson

from pymavlink import mavutil
import droneapi.lib
from droneapi.lib import VehicleMode, Location

import cherrypy
from cherrypy.process import wspbus, plugins
from jinja2 import Environment, FileSystemLoader

ROOT_FOLDER = '/home/user/Droneapi'

class Drone(object):
	def __init__(self, home_coords):
		self.api = local_connect()
		self.vehicle = self.api.get_vehicles()[0]
		self.commands = self.vehicle.commands
		self.altitude = 30

		# Fly drone to home location
		self.vehicle.mode = VehicleMode('GUIDED')
		self.goto(home_coords)

	def goto(self, location, relative=None):
		location_object = Location(
			location[0], location[1],
			self.altitude,
			is_relative=relative
		)
		self.commands.goto(location_object)
		self.vehicle.flush()
		self.current_location = location_object

	def get_location(self):
		return [self.current_location.lat, self.current_location.lon]

class Templates:
	def __init__(self, home_coords):
		self.home_coords = home_coords
		self.options = self.get_options()
		self.environment = Environment(loader=FileSystemLoader( ROOT_FOLDER + 'html'))

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

class Webserver(object):
	def __init__(self):
		home_coords = [32.5738, -117.0068]
		self.templates = Templates(home_coords)
		self.drone = Drone(home_coords)

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
		# Get new coordinates from Vehicle
		current_coords = self.drone.get_location()

		# PROCESS POST REQUEST FROM COMMAND
		if(lat != None and lon != None):
			self.drone.goto([float(lat), float(lon)], True)

		return self.templates.track(current_coords)

conf = {
	'/': {
		'tools.sessions.on': True,
		'tools.staticdir.root': ROOT_FOLDER
	 },
	'/static': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './html/assets'
	}
}

cherrypy.quickstart(Webserver(), '/', conf)
