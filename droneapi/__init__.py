import time
from pymavlink import mavutil

# Clean impl of mp dependencies for droneapi

# Cumulative list of packets we don't yet handle
# TODO: clear this list and handle them!
swallow = ['AHRS', 'AHRS2', 'ATTITUDE', 'EKF_STATUS_REPORT', 'GLOBAL_POSITION_INT',
           'GPS_RAW_INT', 'HWSTATUS', 'MEMINFO', 'MISSION_CURRENT', 'NAV_CONTROLLER_OUTPUT',
           'RAW_IMU', 'RC_CHANNELS_RAW', 'SCALED_IMU2', 'SCALED_PRESSURE', 'SENSOR_OFFSETS',
           'SERVO_OUTPUT_RAW', 'SIMSTATE', 'SYSTEM_TIME', 'SYS_STATUS', 'TERRAIN_REPORT',
           'TERRAIN_REQUEST', 'VFR_HUD', 'STATUSTEXT', 'LOCAL_POSITION_NED', 'COMMAND_ACK']

import droneapi.module.api as api

class FakeAPI:
    def __init__(self, module):
        self.__vehicle = api.MPVehicle(module)
        self.exit = False

    def advertise_mavlink_packet(self, pkt):
        if self.__vehicle.mavrx_callback:
            self.__vehicle.mavrx_callback(pkt)

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

        self.api = None

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

        self.mav_param = {} 

        # Weird
        self.mpstate = self
        self.functions = self

    def module(self, which):
        # psyche
        return self

    def param_set(self, name, value, retries=3):
        # TODO dumbly reimplement this using timeout loops
        # because we should actually be awaiting an ACK of PARAM_VALUE
        # changed, but we don't have a proper ack structure, we'll
        # instead just wait until the value itself was changed

        name = name.upper()
        value = float(value)
        success = False
        while retries > 0:
            retries -= 1
            self.master.param_set_send(name.upper(), value)
            tstart = time.time()
            while time.time() - tstart < 1:
                if self.mav_param[name] == value:
                    return True
                time.sleep(0.1)
        
        print("Timeout setting parameter %s to %f" % (name, value))
        return False

    def prepare(self):
        print('Await heartbeat.')
        # TODO this should be more rigious. How to avoid
        #   invalid MAVLink prefix '73'
        #   invalid MAVLink prefix '13'
        while True:
            try:
                self.master.wait_heartbeat()
                break
            except mavutil.mavlink.MAVError:
                continue
        print('DONE')
        send_heartbeat(self.master)
        request_data_stream_send(self.master)

        params = type('PState',(object,),{
            "mav_param_count": -1,
            "mav_param_set": []
        })()
        self.mav_param = {}
        self.pstate = params
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
                            if params.mav_param_count == -1:
                                params.mav_param_count = msg.param_count
                                params.mav_param_set = [None]*msg.param_count
                            try:
                                if msg.param_index < msg.param_count:
                                    params.mav_param_set[msg.param_index] = msg
                                self.mav_param[msg.param_id] = msg.param_value
                            except:
                                import traceback
                                traceback.print_exc()

                        elif msg.get_type() == 'HEARTBEAT':
                            self.status.armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                            self.status.flightmode = {v: k for k, v in self.master.mode_mapping().items()}[msg.custom_mode]

                        else:
                            print(msg)
                            pass

                    if self.api:
                        self.api.advertise_mavlink_packet(msg)

        t = Thread(target=mavlink_thread)
        t.daemon = True
        t.start()

        while True:
            time.sleep(0.1)
            if params.mav_param_count > 0 and None not in params.mav_param_set:
                print('Completed list of %s params' % (params.mav_param_count,))
                print('Starting dronekit.')
                break

        self.api = FakeAPI(self)
        return self.api

import psutil
def kill(proc_pid):
    try:
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
        process.kill()
    except psutil.NoSuchProcess:
        pass

def local_connect():
    import droneapi.module.api as api
    state = MPFakeState()
    # api.init(state)
    return state.prepare()

import atexit
bg = []
def cleanup_processes():
    for p in bg:
        kill(p.pid)
atexit.register(cleanup_processes)

def sitl_connect():
    import os
    import sys
    from subprocess import Popen, PIPE

    sitl_args = ['dronekit-sitl', 'copter-3.3-rc5', '-I0', '-S', '--model', 'quad', '--home=-35.363261,149.165230,584,353']

    speedup = os.environ.get('TEST_SPEEDUP', '1')
    rate = os.environ.get('TEST_RATE', '200')
    sitl_args += ['--speedup', str(speedup), '-r', str(rate)]

    # Change CPU core affinity.
    # TODO change affinity on osx/linux
    if sys.platform == 'win32':
        # 0x14 = 0b1110 = all cores except cpu 1
        sitl = Popen(['start', '/affinity', '14', '/realtime', '/b', '/wait'] + sitl_args, shell=True, stdout=PIPE, stderr=PIPE)
    else:
        sitl = Popen(sitl_args, stdout=PIPE, stderr=PIPE)
    bg.append(sitl)

    while sitl.poll() == None:
        line = sitl.stdout.readline()
        if 'Waiting for connection' in line:
            break
    if sitl.poll() != None and sitl.returncode != 0:
        print('[runner] ...aborting with SITL error code ' + str(sitl.returncode))
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(sitl.returncode)

    return local_connect()
