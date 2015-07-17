#!/usr/bin/env python

import time
from pymavlink import mavutil

# Clean impl of mp dependencies for droneapi


def send_heartbeat(master):
    master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

def request_data_stream_send(master, rate=1):
    master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, rate, 1)

swallow = ['AHRS', 'AHRS2', 'ATTITUDE', 'EKF_STATUS_REPORT', 'GLOBAL_POSITION_INT',
           'GPS_RAW_INT', 'HWSTATUS', 'MEMINFO', 'MISSION_CURRENT', 'NAV_CONTROLLER_OUTPUT',
           'RAW_IMU', 'RC_CHANNELS_RAW', 'SCALED_IMU2', 'SCALED_PRESSURE', 'SENSOR_OFFSETS',
           'SERVO_OUTPUT_RAW', 'SIMSTATE', 'SYSTEM_TIME', 'SYS_STATUS', 'TERRAIN_REPORT',
           'VFR_HUD', 'STATUSTEXT']

class MPFakeState:
    def __init__(self):
        self.master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        self.command_map = {}
        self.completions = {}

    def loop(self):
        print('Await heartbeat.')
        self.master.wait_heartbeat()
        print('DONE')
        send_heartbeat(self.master)
        request_data_stream_send(self.master)

        params = None
        self.master.mav.param_request_list_send(self.master.target_system, self.master.target_component)

        while True:
            msg = self.master.recv_msg()
            if msg:
                if msg.get_type() not in swallow:
                    if msg.get_type() == 'PARAM_VALUE':
                        if not params:
                            params = [None]*msg.param_count
                        try:
                            params[msg.param_index] = msg
                        except:
                            import traceback
                            traceback.print_exc()
                        if params and None not in params:
                            print('Completed list of %s params' % (len(params),))
                    else:
                        # print(msg)
                        pass
            else:
                time.sleep(0.1)

import droneapi.module.api as api

state = MPFakeState()
api.init(state)
state.loop()
