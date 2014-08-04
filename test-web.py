from droneapi.lib.WebClient import *
import logging

print "Running web test"
logging.basicConfig(level=logging.DEBUG)

def __handleRxMavlink(msg):
    print "MavRx: ", msg

u = LoginInfo()
u.loginName = "test-bob-py"
u.password = "fishpy"
u.email = "kevinh+pytest2@geeksville.com"
u.vehicleId = 'a8098c1a-f86e-11da-bd1a-00112444be1e' # FIXME - store in prefs

w = WebClient(u)
w.connect(__handleRxMavlink)