__author__ = 'anton'

# Camera module
"""
This is a library for controlling cameras. It's a typical thing for companion computers to do,
so it's a handy extensions of dronekit.

The lib is primariliy meant for cams with wifi capability. But USB and Ir might be possible too.

Creating an camera object supposes your computer is connected to the wifi hotspot of the camera you are trying to control

----
"""

from urllib2 import urlopen
from time import localtime

class GoProHero3(object):
    def __init__(self, wifi_password="goprohero3"):
        self.wifipassword = wifi_password

        # See https://github.com/KonradIT/goprowifihack/blob/master/WiFi-Commands.mkdn
        # for a list of http commands to control the GoPro camera

        #TODO: convert these into methods.
        self.on = "http://10.5.5.9/bacpac/PW?t=" + self.wifipassword + "&p=%01"
        self.off = "http://10.5.5.9/bacpac/PW?t=" + self.wifipassword + "&p=%00"
        self.stop = "http://10.5.5.9/bacpac/SH?t=" + self.wifipassword + "&p=%00"
        self.videoMode = "http://10.5.5.9/camera/CM?t=" + self.wifipassword + "&p=%00"
        self.burstMode = "http://10.5.5.9/camera/CM?t=" + self.wifipassword + "&p=%02"
        self.timeLapseMode = "http://10.5.5.9/camera/CM?t=" + self.wifipassword + "&p=%03"
        self.previewOn = "http://10.5.5.9/camera/PV?t=" + self.wifipassword + "&p=%02"
        self.previewOff = "http://10.5.5.9/camera/PV?t=" + self.wifipassword + "&p=%00"
        self.wvga60 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%00"
        self.wvga120 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%01"
        self.v720p30 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%02"
        self.v720p60 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%03"
        self.v960p30 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%04"
        self.v960p48 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%05"
        self.v1080p30 = "http://10.5.5.9/camera/VR?t=" + self.wifipassword + "&p=%06"
        self.viewWide = "http://10.5.5.9/camera/FV?t=" + self.wifipassword + "&p=%00"
        self.viewMedium = "http://10.5.5.9/camera/FV?t=" + self.wifipassword + "&p=%01"
        self.viewNarrow = "http://10.5.5.9/camera/FV?t=" + self.wifipassword + "&p=%02"
        self.res11mpWide = "http://10.5.5.9/camera/PR?t=" + self.wifipassword + "&p=%00"
        self.res8mpMedium = "http://10.5.5.9/camera/PR?t=" + self.wifipassword + "&p=%01"
        self.res5mpWide = "http://10.5.5.9/camera/PR?t=" + self.wifipassword + "&p=%02"
        self.res5mpMedium = "http://10.5.5.9/camera/PR?t=" + self.wifipassword + "&p=%03"
        self.noSound = "http://10.5.5.9/camera/BS?t=" + self.wifipassword + "&p=%00"
        self.sound70 = "http://10.5.5.9/camera/BS?t=" + self.wifipassword + "&p=%01"
        self.sound100 = "http://10.5.5.9/camera/BS?t=" + self.wifipassword + "&p=%02"

        self.sync_time()

    @staticmethod
    def send_cmd(cmd):
        data = urlopen(cmd).read()

    def sync_time(self):
        lt = localtime()
        goprotime = "%{:02x}%{:02x}%{:02x}%{:02x}%{:02x}%{:02x}".format(lt.tm_year-2000,
                                                                        lt.tm_mon,
                                                                        lt.tm_mday,
                                                                        lt.tm_hour,
                                                                        lt.tm_min,
                                                                        lt.tm_sec)
        self.send_cmd("http://10.5.5.9/camera/TM?t=" + self.wifipassword + "&p=" + goprotime)

    def shutter(self):
        self.send_cmd("http://10.5.5.9/bacpac/SH?t=" + self.wifipassword + "&p=%01")

    def photo_mode(self):
        self.send_cmd("http://10.5.5.9/camera/CM?t=" + self.wifipassword + "&p=%01")