from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
from pymavlink import mavutil, mavwp
from Queue import Empty
from pymavlink.dialects.v10 import ardupilotmega
import types

if platform.system() == 'Windows':
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED

# Clean impl of mp dependencies for dronekit

import dronekit.module.api as api

# Public exports
Vehicle = api.MPVehicle

def errprinter(*args):
    print(*args, file=sys.stderr)

class FakeAPI:
    def __init__(self, module):
        self.__vehicle = module.vehicle_class(module)
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
        errprinter('writer should not have had a read request')
        os._exit(43)

def send_heartbeat(master):
    master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

def request_data_stream_send(master, rate=1):
    master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, rate, 1)

from Queue import Queue
from threading import Thread

class MPFakeState:
    def __init__(self, master, vehicle_class=Vehicle):
        self.vehicle_class = vehicle_class

        self.master = master
        out_queue = Queue()
        # self.mav_thread = mav_thread(master, self)
        # self.mav = master.mav

        self.api = None

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue = out_queue
        self.master.mav = mavutil.mavlink.MAVLink(MavWriter(self.out_queue), srcSystem=self.master.source_system, use_native=False)

        self.command_map = {}
        self.completions = {}

        self.target_system = 0
        self.target_component = 0

        self.status = type('MPStatus',(object,),{
            'flightmode': 'AUTO',
            'armed': False,
        })()

        self.mav_param = {} 

        # Weird
        self.mpstate = self
        self.functions = self
        self.mpstate.settings = self

        # waypoints
        self.wploader = mavwp.MAVWPLoader()
        self.wp_loaded = True

        # Attaches message listeners.
        self.message_listeners = dict()

        def message_default(name):
            """
            Decorator for default message handlers.
            """
            def decorator(fn):
                if isinstance(name, list):
                    for n in name:
                        self.on_message(n, fn)
                else:
                    self.on_message(name, fn)
            return decorator

        self.status_printer = None

        @message_default('STATUSTEXT')
        def listener(self, name, m):
            if self.status_printer:
                self.status_printer(re.sub(r'(^|\n)', '>>> \1', m.text.rstrip()))

        self.lat = None
        self.lon = None
        self.alt = None
        self.vx = None
        self.vy = None
        self.vz = None
        
        @message_default('GLOBAL_POSITION_INT')
        def listener(self, name, m):
            (self.lat, self.lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            (self.vx, self.vy, self.vz) = (m.vx / 100.0, m.vy / 100.0, m.vz / 100.0)
            self._notify_attribute_listeners('location', 'velocity')

        @message_default('GPS_RAW')
        def listener(self, name, m):
            # (self.lat, self.lon) = (m.lat, m.lon)
            # self.__on_change('location')
            # better to just use global position int
            pass 

        self.eph = None
        self.epv = None
        self.satellites_visible = None
        self.fix_type = None  # FIXME support multiple GPSs per vehicle - possibly by using componentId
        
        @message_default('GPS_RAW_INT')
        def listener(self, name, m):
            # (self.lat, self.lon) = (m.lat / 1.0e7, m.lon / 1.0e7)
            self.eph = m.eph
            self.epv = m.epv
            self.satellites_visible = m.satellites_visible
            self.fix_type = m.fix_type
            self._notify_attribute_listeners('gps_0')

        self.heading = None
        # self.alt = None
        self.airspeed = None
        self.groundspeed = None
        
        @message_default('VFR_HUD')
        def listener(self, name, m):
            self.heading = m.heading
            self.alt = m.alt
            self.airspeed = m.airspeed
            self.groundspeed = m.groundspeed
            self._notify_attribute_listeners('location', 'airspeed', 'groundspeed')

        self.pitch = None
        self.yaw = None
        self.roll = None
        self.pitchspeed = None
        self.yawspeed = None
        self.rollspeed = None
        
        @message_default('ATTITUDE')
        def listener(self, name, m):
            self.pitch = m.pitch
            self.yaw = m.yaw
            self.roll = m.roll
            self.pitchspeed = m.pitchspeed
            self.yawspeed = m.yawspeed
            self.rollspeed = m.rollspeed
            self._notify_attribute_listeners('attitude')

        self.voltage = -1
        self.current = -1
        self.level = -1
        
        @message_default('SYS_STATUS')
        def listener(self, name, m):
            self.voltage = m.voltage_battery
            self.current = m.current_battery
            self.level = m.battery_remaining
            self._notify_attribute_listeners('battery')

        self.system_status = None

        @message_default('HEARTBEAT')
        def listener(self, name, m):
            self.system_status = m.system_status
            self._notify_attribute_listeners('mode', 'armed')

        self.last_waypoint = 0

        @message_default(['WAYPOINT_CURRENT', 'MISSION_CURRENT'])
        def listener(self, name, m):
            self.last_waypoint = m.seq

        self.rc_readback = {}

        @message_default('RC_CHANNELS_RAW')
        def listener(self, name, m):
            def set(chnum, v):
                '''Private utility for handling rc channel messages'''
                # use port to allow ch nums greater than 8
                self.rc_readback[str(m.port * 8 + chnum)] = v

            set(1, m.chan1_raw)
            set(2, m.chan2_raw)
            set(3, m.chan3_raw)
            set(4, m.chan4_raw)
            set(5, m.chan5_raw)
            set(6, m.chan6_raw)
            set(7, m.chan7_raw)
            set(8, m.chan8_raw)

        self.mount_pitch = None
        self.mount_yaw = None
        self.mount_roll = None

        @message_default('MOUNT_STATUS')
        def listener(self, name, m):
            self.mount_pitch = m.pointing_a / 100
            self.mount_roll = m.pointing_b / 100
            self.mount_yaw = m.pointing_c / 100
            self._notify_attribute_listeners('mount')

        self.rngfnd_distance = None
        self.rngfnd_voltage = None

        @message_default('RANGEFINDER')
        def listener(self, name, m):
            self.rngfnd_distance = m.distance
            self.rngfnd_voltage = m.voltage
            self._notify_attribute_listeners('rangefinder')

        self.ekf_ok = False

        @message_default('EKF_STATUS_REPORT')
        def listener(self, name, m):
            # legacy check for dronekit-python for solo
            # use same check that ArduCopter::system.pde::position_ok() is using

            # boolean: EKF's horizontal position (absolute) estimate is good
            status_poshorizabs = (m.flags & ardupilotmega.EKF_POS_HORIZ_ABS) > 0
            # boolean: EKF is in constant position mode and does not know it's absolute or relative position
            status_constposmode = m.flags & ardupilotmega.EKF_CONST_POS_MODE > 0
            # boolean: EKF's predicted horizontal position (absolute) estimate is good
            status_predposhorizabs = (m.flags & ardupilotmega.EKF_PRED_POS_HORIZ_ABS) > 0

            if self.status.armed:
                self.ekf_ok = status_poshorizabs and not status_constposmode
            else:
                self.ekf_ok = status_poshorizabs or status_predposhorizabs

            self._notify_attribute_listeners('ekf_ok')

    def fetch(self):
        """
        Fetch waypoints.
        """
        self.wp_loaded = False
        self.master.waypoint_request_list_send()

    def send_all_waypoints(self):
        """
        Send waypoints to master.
        """
        self.master.waypoint_clear_all_send()
        if self.wploader.count() > 0:
            self.master.waypoint_count_send(self.wploader.count())

    def fix_targets(self, message):
        pass
        # """Set correct target IDs for our vehicle"""
        # settings = self.mpstate.settings
        # if hasattr(message, 'target_system'):
        #     message.target_system = settings.target_system
        # if hasattr(message, 'target_component'):
        #     message.target_component = settings.target_component

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
        remaining = retries
        while True:
            self.master.param_set_send(name.upper(), value)
            tstart = time.time()
            if remaining == 0:
                break
            remaining -= 1
            while time.time() - tstart < 1:
                if name in self.mav_param and self.mav_param[name] == value:
                    return True
                time.sleep(0.1)
        
        if retries > 0:
            errprinter("timeout setting parameter %s to %f" % (name, value))
        return False

    def __on_change(self, *args):
        for a in args:
            for v in self.api.get_vehicles():
                v.notify_observers(a)

    def _notify_attribute_listeners(self, *args):
        return self.__on_change(*args)

    def on_message(self, name, fn):
        """
        Adds a message listener.
        """
        name = str(name)
        if name not in self.message_listeners:
            self.message_listeners[name] = []
        if fn not in self.message_listeners[name]:
            self.message_listeners[name].append(fn)

    def remove_message_listener(self, name, fn):
        """
        Removes a message listener.
        """
        name = str(name)
        if name in self.message_listeners:
            self.message_listeners[name].remove(fn)
            if len(self.message_listeners[name]) == 0:
                del self.message_listeners[name]

    def mavlink_packet(self, m):
        typ = m.get_type()

        # Call message listeners.
        for fn in self.message_listeners.get(typ, []):
            fn(self, typ, m)
        for fn in self.message_listeners.get('*', []):
            fn(self, typ, m)

        if self.api:
            for v in self.api.get_vehicles():
                if v.mavrx_callback:
                    v.mavrx_callback(m)

    def prepare(self, await_params=False, rate=None):
        # errprinter('Await heartbeat.')
        # TODO this should be more rigious. How to avoid
        #   invalid MAVLink prefix '73'
        #   invalid MAVLink prefix '13'

        params = type('PState',(object,),{
            "mav_param_count": -1,
            "mav_param_set": [],
            "loaded": False,
            "start": False,
        })()
        self.mav_param = {}
        self.pstate = params
        self.api = FakeAPI(self)

        import atexit
        self.exiting = False
        def onexit():
            self.exiting = True
        atexit.register(onexit)

        heartbeat_started = False

        def mavlink_thread():
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                # Record the time we received the last "new" param.
                last_new_param = time.time()
                last_heartbeat_sent = 0
                last_heartbeat_received = 0

                start_duration = 0.2
                repeat_duration = 1
                duration = start_duration

                while True:
                    # Downtime                    
                    time.sleep(0.05)

                    # Parameter watchdog.
                    # Check the time duration for last "new" params exceeds watchdog.
                    if params.start:
                        if None not in params.mav_param_set:
                            params.loaded = True

                        if not params.loaded and time.time() - last_new_param > duration:
                            c = 0
                            for i, v in enumerate(params.mav_param_set):
                                if v == None:
                                    self.master.mav.param_request_read_send(self.master.target_system, self.master.target_component, "", i)
                                    c += 1
                                    if c > 50:
                                        break
                            duration = repeat_duration
                            last_new_param = time.time()

                    # TODO: Waypoint watching / re-requesting

                    # Send 1 heartbeat per second
                    if time.time() - last_heartbeat_sent > 1:
                        send_heartbeat(self.master)
                        last_heartbeat_sent = time.time()
                    # Timeout after 5
                    if heartbeat_started:
                        if last_heartbeat_received == 0:
                            last_heartbeat_received = time.time()
                        elif time.time() - last_heartbeat_received > 5:
                            # raise Exception('Link timeout, no heartbeat in last 5 seconds')
                            errprinter('Link timeout, no heartbeat in last 5 seconds')
                            last_heartbeat_received = time.time()

                    while True:
                        try:
                            msg = self.out_queue.get_nowait()
                            self.master.write(msg)
                        except socket.error as error:
                            if error.errno == ECONNABORTED:
                                errprinter('reestablishing connection after read timeout')
                                try:
                                    self.master.close()
                                except:
                                    pass
                                self.master = mavutil.mavlink_connection(self.master.address)
                                continue

                            # If connection reset (closed), stop polling.
                            return
                        except Empty:
                            break
                        except Exception as e:
                            errprinter('mav send error:', e)
                            break

                    while True:
                        try:
                            msg = self.master.recv_msg()
                        except socket.error as error:
                            if error.errno == ECONNABORTED:
                                errprinter('reestablishing connection after send timeout')
                                try:
                                    self.master.close()
                                except:
                                    pass
                                self.master = mavutil.mavlink_connection(self.master.address)
                                continue

                            # If connection reset (closed), stop polling.
                            return
                        except Exception as e:
                            # TODO debug these.
                            # errprinter('mav recv error:', e)
                            msg = None
                        if not msg:
                            break

                        # Parmater: receive values
                        if msg.get_type() == 'PARAM_VALUE':
                            # If we discover a new param count, assume we
                            # are receiving a new param set.
                            if params.mav_param_count != msg.param_count:
                                params.loaded = False
                                params.start = True
                                params.mav_param_count = msg.param_count
                                params.mav_param_set = [None]*msg.param_count

                            # Attempt to set the params. We throw an error
                            # if the index is out of range of the count or
                            # we lack a param_id.
                            try:
                                if msg.param_index < msg.param_count and msg:
                                    if params.mav_param_set[msg.param_index] == None:
                                        last_new_param = time.time()
                                        duration = start_duration
                                    params.mav_param_set[msg.param_index] = msg
                                self.mav_param[msg.param_id] = msg.param_value
                            except:
                                import traceback
                                traceback.print_exc()

                        # Waypoint receive
                        if not self.wp_loaded:
                            if msg.get_type() in ['WAYPOINT_COUNT','MISSION_COUNT']:
                                self.wploader.clear()
                                self.wploader.expected_count = msg.count
                                self.master.waypoint_request_send(0)
                            if msg.get_type() in ['WAYPOINT', 'MISSION_ITEM']:
                                if msg.seq > self.wploader.count():
                                    # Unexpected waypoint
                                    pass
                                elif msg.seq < self.wploader.count():
                                    # Waypoint duplicate
                                    pass
                                else:
                                    self.wploader.add(msg)

                                    if msg.seq + 1 < self.wploader.expected_count:
                                        self.master.waypoint_request_send(msg.seq + 1)
                                    else:
                                        self.wp_loaded = True
                        if msg.get_type() in ["WAYPOINT_CURRENT", "MISSION_CURRENT"]:
                            self.last_waypoint = msg.seq

                        # Waypoint send to master
                        # TODO
                        if msg.get_type() in ["WAYPOINT_REQUEST", "MISSION_REQUEST"]:
                            pass

                        # Heartbeat: armed + mode update
                        if msg.get_type() == 'HEARTBEAT':
                            self.status.armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                            self.status.flightmode = {v: k for k, v in self.master.mode_mapping().items()}[msg.custom_mode]
                            last_heartbeat_received = time.time()

                        if self.api:
                            self.mavlink_packet(msg)

            except Exception as e:
                # http://bugs.python.org/issue1856
                if self.exiting:
                    pass
                else:
                    raise


        t = Thread(target=mavlink_thread)
        t.daemon = True
        t.start()
        self.mavlink_thread = t

        # Wait for first heartbeat.
        while True:
            try:
                self.master.wait_heartbeat()
                break
            except mavutil.mavlink.MAVError:
                continue
        heartbeat_started = True

        # Request a list of all parameters.
        if rate != None:
            request_data_stream_send(self.master, rate=rate)
        while True:
            # This fn actually rate limits itself to every 2s.
            # Just retry with persistence to get our first param stream.
            self.master.param_fetch_all()
            time.sleep(0.1)
            if params.mav_param_count > -1:
                break

        # We now should get parameters streaming in.
        # We may not get the full set; we leave the logic to mavlink_thread
        # to determine what params we yet need. Wait if await_params is True.
        if await_params:
            while not params.loaded:
                time.sleep(0.1)

        return self.api

    def close(self):
        # TODO this can block forever if parameters continue to be added
        self.exiting = True
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.master.close()

def connect(ip, await_params=False, status_printer=errprinter, vehicle_class=Vehicle, rate=4):
    import dronekit.module.api as api
    state = MPFakeState(mavutil.mavlink_connection(ip), vehicle_class=vehicle_class)
    state.status_printer = status_printer
    # api.init(state)
    return state.prepare(await_params=await_params, rate=rate).get_vehicles()[0]
