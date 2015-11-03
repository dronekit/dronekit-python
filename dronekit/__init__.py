from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
import dronekit.lib
from pymavlink import mavutil, mavwp
from Queue import Queue, Empty
from threading import Thread
import types

if platform.system() == 'Windows':
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED

# Public re-exports
Vehicle = dronekit.lib.Vehicle
Command = dronekit.lib.Command
CommandSequence = dronekit.lib.CommandSequence
VehicleMode = dronekit.lib.VehicleMode
LocationGlobal = dronekit.lib.LocationGlobal
LocationLocal = dronekit.lib.LocationLocal
CloudClient = dronekit.lib.CloudClient

def errprinter(*args):
    print(*args, file=sys.stderr)

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

class MPFakeState:
    def __init__(self, master, vehicle_class=Vehicle):
        self.vehicle_class = vehicle_class

        self.master = master
        self.vehicle = None

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue = Queue()
        self.master.mav = mavutil.mavlink.MAVLink(MavWriter(self.out_queue), srcSystem=self.master.source_system, use_native=False)

        # Targets
        self.target_system = 0
        self.target_component = 0

        # Parameters
        self.mav_param = {} 

        self.vehicle = self.vehicle_class(self)

    def fix_targets(self, message):
        pass
        # """Set correct target IDs for our vehicle"""
        # if hasattr(message, 'target_system'):
        #     message.target_system = self.target_system
        # if hasattr(message, 'target_component'):
        #     message.target_component = self.target_component

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
            self.vehicle.notify_observers(a)

    def _notify_attribute_listeners(self, *args):
        return self.__on_change(*args)

    def mavlink_packet(self, m):
        typ = m.get_type()

        # Downstream.
        for fn in self.vehicle.message_listeners.get(typ, []):
            fn(self.vehicle, typ, m)
        for fn in self.vehicle.message_listeners.get('*', []):
            fn(self.vehicle, typ, m)

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
                                if self.master.reset:
                                    self.master.reset()
                                else:
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
                                if self.master.reset:
                                    self.master.reset()
                                else:
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

                        # Heartbeat: armed + mode update
                        if msg.get_type() == 'HEARTBEAT':
                            last_heartbeat_received = time.time()

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

            # Await GPS lock
            while self.vehicle._fix_type == None:
                time.sleep(0.1)

    def close(self):
        # TODO this can block forever if parameters continue to be added
        self.exiting = True
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.master.close()

def connect(ip, await_params=False, status_printer=errprinter, vehicle_class=Vehicle, rate=4, baud=115200):
    state = MPFakeState(mavutil.mavlink_connection(ip, baud=baud), vehicle_class=vehicle_class)

    if status_printer:
        print('ok')
        @state.vehicle.message_listener('STATUSTEXT')
        def listener(self, name, m):
            status_printer(re.sub(r'(^|\n)', '>>> ', m.text.rstrip()))
    
    state.prepare(await_params=await_params, rate=rate)
    return state.vehicle
