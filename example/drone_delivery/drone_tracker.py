import os, os.path
import random
import simplejson
import time
import math
import numpy
import pid
#import ansicolors
import pdb

from pymavlink import mavutil
import droneapi.lib
from droneapi.lib import VehicleMode, Location

import cherrypy
from cherrypy.process import wspbus, plugins
from jinja2 import Environment, FileSystemLoader

def get_fake_coords():
	return [
		[-117.03426361083983, 32.604675440554985],
		[-117.01692581176758, 32.592527461735294],
		[-117.00834274291992, 32.59325060181434],
		[-116.99838638305664, 32.59122579488824],
		[-116.99718475341797, 32.58601893844575],
		[-116.99769973754883, 32.579799241291816],
		[-116.9992446899414, 32.57531500590736],
		[-117.00662612915038, 32.57502569269813]
	]

class DroneTrackerPlugin(plugins.SimplePlugin):
	def __init__(self, bus, drone_klass):
		plugins.SimplePlugin.__init__(self, bus)
		self.drone = drone_klass()

	def start(self):
		self.bus.log('DroneAPI Start')

	def stop(self):
		self.bus.log('DroneAPI Stop')

class Drone(object):
	def __init__(self):
		#pdb.set_trace()
		self.init_time = time.time()
		self.api = droneapi.lib.local_connect()
		self.vehicle = self.api.get_vehicles()[0]

class Templates:
	def __init__(self):
		self.options = self.get_options()
		self.environment = Environment(loader=FileSystemLoader('html'))

	def get_options(self):
		return {
			'width': 670,
			'height': 470,
			'zoom': 13,
			'format': 'png',
			'access_token': 'pk.eyJ1IjoibXJwb2xsbyIsImEiOiJtUG0tRk9BIn0.AqAiefUV9fFYRo-w0jFR1Q',
			'mapid': 'mrpollo.kfbnjbl0',
			'home_coords': [-117.0068, 32.5738],
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
		json = simplejson.dumps(self.options)
		self.options['json'] = json
		return self.get_template('track')

	def command(self):
		self.options = self.get_options()
		self.options['current_url'] = '/command'
		return self.get_template('command')

	def get_template(self, file_name):
		template = self.environment.get_template( file_name + '.html')
		return template.render(options=self.options)

	index.exposed = True


class Webserver(object):
	def __init__(self):
		self.templates = Templates()
		DroneTrackerPlugin(cherrypy.engine, Drone).subscribe()

	@cherrypy.expose
	def index(self):
		return self.templates.index()

	@cherrypy.expose
	def track(self, lat=None, lon=None):
		# FIX RANDOM COORDS
		random_current_coords = get_fake_coords()
		random.shuffle(random_current_coords)
		current_coords = random_current_coords[0]

		return self.templates.track(current_coords)

	@cherrypy.expose
	def command(self):
		return self.templates.command()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def vehicle(self):
		# FIX RANDOM COORDS
		random_current_coords = get_fake_coords()
		random.shuffle(random_current_coords)
		current_coords = random_current_coords[0]

		# TOTALLY FAKE DATA
		# NEED TO REMOVE THIS
		# AND FIX THE PARAM NAMES
		# FOR VEHICLE UPDATES
		return dict(name='cool copter', position=current_coords)

#if __name__ == '__main__':
conf = {
	'/': {
		'tools.sessions.on': True,
		'tools.staticdir.root': os.path.abspath(os.getcwd())
	 },
	'/static': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': './html/assets'
	}
}
cherrypy.quickstart(Webserver(), '/', conf)
