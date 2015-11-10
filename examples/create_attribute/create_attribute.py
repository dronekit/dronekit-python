"""
create_attribute.py:

Demonstrates how to create attributes for MAVLink messages within your DroneKit-Python script 
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
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()

# Connect to our custom vehicle_class MyVehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True, vehicle_class=MyVehicle)

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
