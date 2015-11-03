from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
import dronekit.lib
from dronekit.tools import errprinter
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

class MavWriter():
    def __init__(self, queue):
        self.queue = queue

    def write(self, pkt):
        self.queue.put(pkt)

    def read(self):
        errprinter('writer should not have had a read request')
        os._exit(43)

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

        # Event loop listeners.
        self.loop_listeners = []

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

    def loop_listener(self, fn):
        """
        Decorator for event loop.
        """
        self.loop_listeners.append(fn)

    def prepare(self, await_params=False, rate=None):
        # errprinter('Await heartbeat.')
        # TODO this should be more rigious. How to avoid
        #   invalid MAVLink prefix '73'
        #   invalid MAVLink prefix '13'

        import atexit
        self.exiting = False
        def onexit():
            self.exiting = True
        atexit.register(onexit)

        def mavlink_thread():
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                while True:
                    # Downtime                    
                    time.sleep(0.05)

                    # Loop listeners.
                    for fn in self.loop_listeners:
                        fn(self)

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
            if self.vehicle._params_count > -1:
                break

        # We now should get parameters streaming in.
        # We may not get the full set; we leave the logic to mavlink_thread
        # to determine what params we yet need. Wait if await_params is True.
        if await_params:
            while not self.vehicle._params_loaded:
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
