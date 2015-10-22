"""
create_attribute.py:

Demonstrates how to create attributes for MAVLink messages within your DroneKit-Python script 
and use them in the same way as the built-in Vehicle attributes.

The code adds a new attribute to the Vehicle class, populating it with information from RAW_IMU messages 
intercepted using set_mavlink_callback.

Full documentation is provided at http://python.dronekit.io/examples/create_attribute.html
"""

from dronekit import connect
from dronekit.lib import VehicleMode
from pymavlink import mavutil
import time


#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, await_params=True)



class RawIMU(object):
    """
    The RAW IMU readings for the usual 9DOF sensor setup. 
    This contains the true raw values without any scaling to allow data capture and system debugging.
    
    The message definition is here: https://pixhawk.ethz.ch/mavlink/#RAW_IMU
    
    :param time_boot_us: Timestamp (microseconds since system boot). #Note, not milliseconds as per spec
    :param xacc: X acceleration (mg)
    :param yacc: Y acceleration (mg)
    :param zacc: Z acceleration (mg)
    :param xgyro: Angular speed around X axis (millirad /sec)
    :param ygyro: Angular speed around Y axis (millirad /sec)
    :param zgyro: Angular speed around Z axis (millirad /sec)
    :param xmag: X Magnetic field (milli tesla)
    :param ymag: Y Magnetic field (milli tesla)
    :param zmag: Z Magnetic field (milli tesla)    
    """
    def __init__(self, time_boot_us, xacc, yacc, zacc, xygro, ygyro, zgyro, xmag, ymag, zmag):
        """
        RawIMU object constructor.
        """
        self.time_boot_us = time_boot_us
        self.xacc = xacc
        self.yacc = yacc
        self.zacc = zacc
        self.xgyro = zgyro
        self.ygyro = ygyro
        self.zgyro = zgyro
        self.xmag = xmag        
        self.ymag = ymag
        self.zmag = zmag      
        
    def __str__(self):
        """
        String representation used to print the RawIMU object. 
        """
        return "RAW_IMU: time_boot_us={},xacc={},yacc={},zacc={},xgyro={},ygyro={},zgyro={},xmag={},ymag={},zmag={}".format(self.time_boot_us, self.xacc, self.yacc,self.zacc,self.xgyro,self.ygyro,self.zgyro,self.xmag,self.ymag,self.zmag)

   

#Create an Vehicle.raw_imu object and set all values to None.
vehicle.raw_imu=RawIMU(None,None,None,None,None,None,None,None,None,None)


def mav_raw_imu_handler(message):
    """
    Writes received message to the (newly attached) vehicle.raw_imu object and notifies observers.
    """
    messagetype=str(message).split('{')[0].strip()
    if messagetype=='RAW_IMU':
        vehicle.raw_imu.time_boot_us=message.time_usec
        vehicle.raw_imu.xacc=message.xacc
        vehicle.raw_imu.yacc=message.yacc
        vehicle.raw_imu.zacc=message.zacc
        vehicle.raw_imu.xgyro=message.xgyro
        vehicle.raw_imu.ygyro=message.ygyro
        vehicle.raw_imu.zgyro=message.zgyro
        vehicle.raw_imu.xmag=message.xmag
        vehicle.raw_imu.ymag=message.ymag
        vehicle.raw_imu.zmag=message.zmag

        #Add Notify all observers of new message.
        vehicle.notify_observers('raw_imu') 

        
def mavrx_debug_handler(message):
    """
    Handler for MAVLink messages.
    """
    #Handle raw_imu messages
    mav_raw_imu_handler(message)

# Set MAVLink callback handler (after getting Vehicle instance)
vehicle.set_mavlink_callback(mavrx_debug_handler)

"""
From this point vehicle.raw_imu can be used just like any other attribute.
"""

#Callback to print the raw_imu
def raw_imu_callback(rawimu):
    print vehicle.raw_imu


#Add observer for the vehicle's current location
vehicle.add_attribute_observer('raw_imu', raw_imu_callback)

print 'Display RAW_IMU messages for 5 seconds and then exit.'
time.sleep(5)

#The observer can be unset using ``vehicle.unset_mavlink_callback()`` OR 
# ``vehicle.set_mavlink_callback(None)``. 
#It is automatically removed when the thread exits.


#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()