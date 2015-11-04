from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
import dronekit.lib
from dronekit.util import errprinter
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

class MAVHandler:
    def __init__(self, master, vehicle_class=Vehicle):
        self.vehicle_class = vehicle_class

        self.master = master

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue = Queue()
        self.master.mav = mavutil.mavlink.MAVLink(MavWriter(self.out_queue), srcSystem=self.master.source_system, use_native=False)

        # Targets
        self.target_system = 0
        self.target_component = 0

        # Listeners.
        self.loop_listeners = []
        self.message_listeners = []

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
                            self.fix_targets(msg)
                            self.master.write(msg)
                        except socket.error as error:
                            if error.errno == ECONNABORTED:
                                errprinter('reestablishing connection after read timeout')
                                if hasattr(self.master, 'reset'):
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
                                if hasattr(self.master, 'reset'):
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
                            # TODO this should be more rigorous. How to avoid
                            #   invalid MAVLink prefix '73'
                            #   invalid MAVLink prefix '13'
                            # errprinter('mav recv error:', e)
                            msg = None
                        if not msg:
                            break

                        # Message listeners.
                        for fn in self.message_listeners:
                            fn(self, msg)

            except Exception as e:
                # http://bugs.python.org/issue1856
                if self.exiting:
                    pass
                else:
                    raise

        t = Thread(target=mavlink_thread)
        t.daemon = True
        self.mavlink_thread = t

    def fix_targets(self, message):
        """Set correct target IDs for our vehicle"""
        if hasattr(message, 'target_system'):
            message.target_system = self.target_system
        if hasattr(message, 'target_component'):
            message.target_component = self.target_component

    def loop_listener(self, fn):
        """
        Decorator for event loop.
        """
        self.loop_listeners.append(fn)

    def message_listener(self, fn):
        """
        Decorator for message inputs.
        """
        self.message_listeners.append(fn)

    def start(self):
        if not self.mavlink_thread.is_alive():
            self.mavlink_thread.start()

    def close(self):
        # TODO this can block forever if parameters continue to be added
        self.exiting = True
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.master.close()

def connect(ip, wait_ready=None, status_printer=errprinter, vehicle_class=Vehicle, rate=4, baud=115200):
    handler = MAVHandler(mavutil.mavlink_connection(ip, baud=baud))
    vehicle = vehicle_class(handler)

    if status_printer:
        @vehicle.message_listener('STATUSTEXT')
        def listener(self, name, m):
            status_printer(re.sub(r'(^|\n)', '>>> ', m.text.rstrip()))
    
    vehicle.initialize(rate=rate)

    if wait_ready:
        if wait_ready == True:
            vehicle.wait_ready(True)
        else:
            vehicle.wait_ready(*wait_ready)

    return vehicle
