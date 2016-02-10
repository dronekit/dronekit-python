"""
create_attribute.py:

Demonstrates how to create attributes from MAVLink messages within your DroneKit-Python script 
and use them in the same way as the built-in Vehicle attributes.

The code adds a new attribute to the Vehicle class, populating it with information from RAW_IMU messages 
intercepted using the message_listener decorator.

Full documentation is provided at http://python.dronekit.io/examples/create_attribute.html
"""

from dronekit import connect, Vehicle
from my_vehicle import MyVehicle #Our custom vehicle class
import time



#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Demonstrates how to create attributes from MAVLink messages. ')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not args.connect:
    print "Starting copter simulator (SITL)"
    from dronekit_sitl import SITL
    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = ['-I0', '--model', 'quad', '--home=-35.363261,149.165230,584,353']
    sitl.launch(sitl_args, await_ready=True, restart=True)
    connection_string = 'tcp:127.0.0.1:5760'


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True, vehicle_class=MyVehicle)

# Add observer for the custom attribute

def raw_imu_callback(self, attr_name, value):
    # attr_name == 'raw_imu'
    # value == vehicle.raw_imu
    print value

vehicle.add_attribute_listener('raw_imu', raw_imu_callback)

print 'Display RAW_IMU messages for 5 seconds and then exit.'
time.sleep(5)

#The message listener can be unset using ``vehicle.remove_message_listener``

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()
