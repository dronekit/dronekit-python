#
# This is a small example of the python drone API - an ultra minimal GCS
#

from dronekit import connect, VehicleMode
from pymavlink import mavutil
from Tkinter import *

# The tkinter root object
global root

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Tracks GPS position of your computer (Linux only). Connects to SITL on local PC by default.')
parser.add_argument('--connect', default='127.0.0.1:14550',
                   help="vehicle connection target. Default '127.0.0.1:14550'")
args = parser.parse_args()


# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % args.connect
vehicle = connect(args.connect, wait_ready=True)

def setMode(mode):
    # Now change the vehicle into auto mode
    vehicle.mode = VehicleMode(mode)


def updateGUI(label, value):
    label['text'] = value

def addObserverAndInit(name, cb):
    """We go ahead and call our observer once at startup to get an initial value"""
    cb(name)
    vehicle.add_attribute_observer(name, cb)

root = Tk()
root.wm_title("microGCS - the worlds crummiest GCS")
frame = Frame(root)
frame.pack()

locationLabel = Label(frame, text = "No location", width=60)
locationLabel.pack()
attitudeLabel = Label(frame, text = "No Att", width=60)
attitudeLabel.pack()
modeLabel = Label(frame, text = "mode")
modeLabel.pack()

addObserverAndInit('attitude', lambda attr: updateGUI(attitudeLabel, vehicle.attitude))
addObserverAndInit('location', lambda attr: updateGUI(locationLabel, vehicle.location))
addObserverAndInit('mode', lambda attr: updateGUI(modeLabel, vehicle.mode))

Button(frame, text = "Auto", command = lambda : setMode("AUTO")).pack()
Button(frame, text = "RTL", command = lambda : setMode("RTL")).pack()

root.mainloop()