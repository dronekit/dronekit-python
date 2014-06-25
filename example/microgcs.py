#
# This is a small example of the python drone API - an ultra minimal GCS
# Usage:
# * mavproxy.py --master=/dev/ttyACM0,115200
# * module load api
# * api start microgcs.py
#
from droneapi.lib import VehicleMode
from pymavlink import mavutil
from Tkinter import *

# The tkinter root object
global root

# First get an instance of the API endpoint
api = local_connect()
# get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
v = api.get_vehicles()[0]

def setMode(mode):
    # Now change the vehicle into auto mode
    v.mode = VehicleMode(mode)

    # Always call flush to guarantee that previous writes to the vehicle have taken place
    v.flush()

def updateGUI(label, value):
    label['text'] = value

def addObserverAndInit(name, cb):
    """We go ahead and call our observer once at startup to get an initial value"""
    cb(name)
    v.add_attribute_observer(name, cb)

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

addObserverAndInit('attitude', lambda attr: updateGUI(attitudeLabel, v.attitude))
addObserverAndInit('location', lambda attr: updateGUI(locationLabel, v.location))
addObserverAndInit('mode', lambda attr: updateGUI(modeLabel, v.mode))

Button(frame, text = "Auto", command = lambda : setMode("AUTO")).pack()
Button(frame, text = "RTL", command = lambda : setMode("RTL")).pack()

root.mainloop()