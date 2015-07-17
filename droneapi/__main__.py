#!/usr/bin/env python

import time
from pymavlink import mavutil

# Clean impl of mp dependencies for droneapi

swallow = ['AHRS', 'AHRS2', 'ATTITUDE', 'EKF_STATUS_REPORT', 'GLOBAL_POSITION_INT',
           'GPS_RAW_INT', 'HWSTATUS', 'MEMINFO', 'MISSION_CURRENT', 'NAV_CONTROLLER_OUTPUT',
           'RAW_IMU', 'RC_CHANNELS_RAW', 'SCALED_IMU2', 'SCALED_PRESSURE', 'SENSOR_OFFSETS',
           'SERVO_OUTPUT_RAW', 'SIMSTATE', 'SYSTEM_TIME', 'SYS_STATUS', 'TERRAIN_REPORT',
           'VFR_HUD', 'STATUSTEXT', 'LOCAL_POSITION_NED']

def demo(local_connect):
    # This example shows how to use DroneKit-Python to get and set vehicle state, parameter and channel-override information. 
    # It also demonstrates how to observe vehicle attribute (state) changes. 
    # 
    # Usage:
    # * mavproxy.py
    # * module load api
    # * api start vehicle-state.py
    #
    from droneapi.lib import VehicleMode
    from pymavlink import mavutil
    import time

    # First get an instance of the API endpoint
    api = local_connect()
    # Get the connected vehicle (currently only one vehicle can be returned).
    v = api.get_vehicles()[0]

    # Get all vehicle attributes (state)
    print "\nGet all vehicle attribute values:"
    print " Location: %s" % v.location
    print " Attitude: %s" % v.attitude
    print " Velocity: %s" % v.velocity
    print " GPS: %s" % v.gps_0
    print " Groundspeed: %s" % v.groundspeed
    print " Airspeed: %s" % v.airspeed
    print " Mount status: %s" % v.mount_status
    print " Battery: %s" % v.battery
    print " Mode: %s" % v.mode.name    # settable
    print " Armed: %s" % v.armed    # settable

    # Set vehicle mode and armed attributes (the only settable attributes)
    print "Set Vehicle.mode=GUIDED (currently: %s)" % v.mode.name 
    v.mode = VehicleMode("GUIDED")
    v.flush()  # Flush to guarantee that previous writes to the vehicle have taken place
    while not v.mode.name=='GUIDED' and not api.exit:  #Wait until mode has changed
        print " Waiting for mode change ..."
        time.sleep(1)

    print "Set Vehicle.armed=True (currently: %s)" % v.armed 
    v.armed = True
    v.flush()
    while not v.armed and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)


    # Show how to add and remove and attribute observer callbacks (using mode as example) 
    def mode_callback(attribute):
        print " CALLBACK: Mode changed to: ", v.mode.name

    print "\nAdd mode attribute observer for Vehicle.mode" 
    v.add_attribute_observer('mode', mode_callback) 

    print " Set mode=STABILIZE (currently: %s)" % v.mode.name 
    v.mode = VehicleMode("STABILIZE")
    v.flush()

    print " Wait 2s so callback invoked before observer removed"
    time.sleep(2)

    # Remove observer - specifying the attribute and previously registered callback function
    v.remove_attribute_observer('mode', mode_callback)  

    # TODO
    #
    #
    #
    return


    #  Get Vehicle Home location ((0 index in Vehicle.commands)
    print "\nGet home location" 
    cmds = v.commands
    cmds.download()
    cmds.wait_valid()
    print " Home WP: %s" % cmds[0]


    #  Get/Set Vehicle Parameters
    print "\nRead vehicle param 'THR_MIN': %s" % v.parameters['THR_MIN']
    print "Write vehicle param 'THR_MIN' : 10"
    v.parameters['THR_MIN']=10
    v.flush()
    print "Read new value of param 'THR_MIN': %s" % v.parameters['THR_MIN']


    # Overriding an RC channel
    # NOTE: CHANNEL OVERRIDES may be useful for simulating user input and when implementing certain types of joystick control. 
    #DO NOT use unless there is no other choice (there almost always is!)
    print "\nOverriding RC channels for roll and yaw"
    v.channel_override = { "1" : 900, "4" : 1000 }
    v.flush()
    print " Current overrides are:", v.channel_override
    print " Channel default values:", v.channel_readback  # All channel values before override

    # Cancel override by setting channels to 0
    print " Cancelling override"
    v.channel_override = { "1" : 0, "4" : 0 }
    v.flush()


    ## Reset variables to sensible values.
    print "\nReset vehicle atributes/parameters and exit"
    v.mode = VehicleMode("STABILIZE")
    v.armed = False
    v.parameters['THR_MIN']=130
    v.flush()

import droneapi.module.api as api

class FakeAPI:
    def __init__(self, module):
        self.__vehicle = api.MPVehicle(module)
        self.exit = False

    def get_vehicles(self, query=None):
        return [ self.__vehicle ]

# def mav_thread(conn, state):

#     return (in_queue, out_queue)

class MavWriter():
    def __init__(self, queue):
        self.queue = queue

    def write(self, pkt):
        self.queue.put(pkt)

    def read(self):
        print('WTF')
        import os
        os._exit(43)

def send_heartbeat(master):
    master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

def request_data_stream_send(master, rate=1):
    master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, rate, 1)

from Queue import Queue
from threading import Thread

class MPFakeState:
    def __init__(self):
        self.master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        out_queue = Queue()
        # self.mav_thread = mav_thread(master, self)
        # self.mav = master.mav

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for droneapi
        self.out_queue = out_queue
        self.master.mav = mavutil.mavlink.MAVLink(MavWriter(self.out_queue), srcSystem=self.master.source_system, use_native=False)

        self.command_map = {}
        self.completions = {}

        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.pitch = 0
        self.yaw = 0
        self.roll = 0
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.eph = 0
        self.epv = 0
        self.fix_type = ''
        self.satellites_visible = 0
        self.groundspeed = 0
        self.airspeed = 0
        self.mount_pitch = 0
        self.mount_yaw = 0
        self.mount_roll = 0
        self.voltage = 0
        self.current = 0
        self.level = 0
        self.status = type('MPStatus',(object,),{
            'flightmode': 'AUTO',
            'armed': False,
        })()
        self.mpstate = self

    def loop(self):
        print('Await heartbeat.')
        self.master.wait_heartbeat()
        print('DONE')
        send_heartbeat(self.master)
        request_data_stream_send(self.master)

        params = {
            "values": None
        }
        self.master.mav.param_request_list_send(self.master.target_system, self.master.target_component)

        def mavlink_thread():
            while True:
                time.sleep(0.1)

                while True:
                    try:
                        msg = self.out_queue.get_nowait()
                        self.master.write(msg)
                    except:
                        break

                while True:
                    try:
                        msg = self.master.recv_msg()
                    except Exception as e:
                        print(e)
                        msg = None
                    if not msg:
                        break

                    if msg.get_type() not in swallow:
                        if msg.get_type() == 'PARAM_VALUE':
                            if not params['values']:
                                params['values'] = [None]*msg.param_count
                            try:
                                params['values'][msg.param_index] = msg
                            except:
                                import traceback
                                traceback.print_exc()

                        elif msg.get_type() == 'HEARTBEAT':
                            self.status.armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                            self.status.flightmode = {v: k for k, v in self.master.mode_mapping().items()}[msg.custom_mode]

                        else:
                            print(msg)
                            pass

        t = Thread(target=mavlink_thread)
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.1)
            if params['values'] and None not in params['values']:
                print('Completed list of %s params' % (len(params['values']),))
                print('Starting dronekit.')

                def local_connect():
                    return FakeAPI(self)

                demo(local_connect)
                break

import droneapi.module.api as api

state = MPFakeState()
api.init(state)
state.loop()
