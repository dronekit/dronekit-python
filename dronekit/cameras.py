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
import signal
from . import errprinter
import logging

class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()


class GeoTagger(object):
    def __init__(self, vehicle=None):
        self.vehicle = vehicle
        FORMAT = '%(asctime)s, %(message)s'
        DATEFORMAT = "%d-%m-%Y, %H:%M:%S"
        logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT, filename="camera_log.csv", filemode='w', level=logging.INFO)
        logging.info("picture number, waypoint, gimbal pitch, gimbal yaw, gimbal roll, att pitch, att yaw, att roll, latitude, longitude, altitude, camera message")

    def log_vehicle_state(self, num_picture, cam_message):
        if self.vehicle:
            log_msg = ",".join(map(str,[num_picture, self.vehicle.commands.next,
                                        self.vehicle.gimbal.pitch,
                                        self.vehicle.gimbal.yaw,
                                        self.vehicle.gimbal.roll,
                                        self.vehicle.attitude.pitch,
                                        self.vehicle.attitude.yaw,
                                        self.vehicle.attitude.roll,
                                        self.vehicle.location.global_frame.lat,
                                        self.vehicle.location.global_frame.lon,
                                        self.vehicle.location.global_frame.alt,
                                        cam_message
                                        ]))
        else:
            log_msg = str(num_picture)
        logging.info(log_msg)
        pass


def send_http_cmd(cmd):
    try:
        with Timeout(1):
            data = urlopen(cmd).read()
            return data
    except Exception as e:
            errprinter('>>> Exception in http command: ' + str(e))
            return str(e)


class GoProHero3(object):
    def __init__(self, wifi_password="goprohero3", geotag=True, myvehicle=None):
        self.wifipassword = wifi_password
        self.num_picture = 0
        self.geotagger = None
        if geotag:
            self.geotagger = GeoTagger(vehicle=myvehicle)

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


    def sync_time(self):
        lt = localtime()
        goprotime = "%{:02x}%{:02x}%{:02x}%{:02x}%{:02x}%{:02x}".format(lt.tm_year-2000,
                                                                        lt.tm_mon,
                                                                        lt.tm_mday,
                                                                        lt.tm_hour,
                                                                        lt.tm_min,
                                                                        lt.tm_sec)
        send_http_cmd("http://10.5.5.9/camera/TM?t=" + self.wifipassword + "&p=" + goprotime)

    def shutter(self):
        self.num_picture +=1
        result = send_http_cmd("http://10.5.5.9/bacpac/SH?t=" + self.wifipassword + "&p=%01")
        if self.geotagger:
            self.geotagger.log_vehicle_state(self.num_picture, result)



    def photo_mode(self):
        send_http_cmd("http://10.5.5.9/camera/CM?t=" + self.wifipassword + "&p=%01")