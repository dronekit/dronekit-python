from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
import copy
import dronekit
from dronekit import APIException
from dronekit.util import errprinter
from pymavlink import mavutil, mavwp
from Queue import Queue, Empty
from threading import Thread
import types

if platform.system() == 'Windows':
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED


class MAVWriter(object):
    def __init__(self, queue):
        self.queue = queue

    def write(self, pkt):
        self.queue.put(pkt)

    def read(self):
        errprinter('writer should not have had a read request')
        os._exit(43)


class MAVConnection(object):
    def __init__(self, ip, baud=115200, target_system=0, source_system=255):
        self.master = mavutil.mavlink_connection(ip, baud=baud, source_system=source_system)

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue = Queue()
        self.master.mav = mavutil.mavlink.MAVLink(
            MAVWriter(self.out_queue),
            srcSystem=self.master.source_system,
            use_native=False)

        # Monkey-patch MAVLink object for fix_targets.
        sendfn = self.master.mav.send

        def newsendfn(mavmsg):
            self.fix_targets(mavmsg)
            return sendfn(mavmsg)

        self.master.mav.send = newsendfn

        # Targets
        self.target_system = target_system

        # Listeners.
        self.loop_listeners = []
        self.message_listeners = []

        # Debug flag.
        self._accept_input = True
        self._alive = True
        self._death_error = None

        import atexit

        def onexit():
            self._alive = False

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
                            # If connection reset (closed), stop polling.
                            if error.errno == ECONNABORTED:
                                raise APIException('Connection aborting during read')
                            raise
                        except Empty:
                            break
                        except Exception as e:
                            errprinter('>>> mav send error:', e)
                            break

                    while self._accept_input:
                        try:
                            msg = self.master.recv_msg()
                        except socket.error as error:
                            # If connection reset (closed), stop polling.
                            if error.errno == ECONNABORTED:
                                raise APIException('Connection aborting during send')
                            raise
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
                            try:
                                fn(self, msg)
                            except Exception as e:
                                errprinter('>>> Exception in message handler for %s' %
                                           msg.get_type())
                                errprinter('>>> ' + str(e))

            except APIException as e:
                errprinter('>>> ' + str(e.message))
                self._alive = False
                self.master.close()
                self._death_error = e
                return

            except Exception as e:
                # http://bugs.python.org/issue1856
                if not self._alive:
                    pass
                else:
                    self._alive = False
                    self.master.close()
                    self._death_error = e

        t = Thread(target=mavlink_thread)
        t.daemon = True
        self.mavlink_thread = t

    def reset(self):
        self.out_queue = Queue()
        if hasattr(self.master, 'reset'):
            self.master.reset()
        else:
            try:
                self.master.close()
            except:
                pass
            self.master = mavutil.mavlink_connection(self.master.address)

    def fix_targets(self, message):
        """Set correct target IDs for our vehicle"""
        if hasattr(message, 'target_system'):
            message.target_system = self.target_system

    def forward_loop(self, fn):
        """
        Decorator for event loop.
        """
        self.loop_listeners.append(fn)

    def forward_message(self, fn):
        """
        Decorator for message inputs.
        """
        self.message_listeners.append(fn)

    def start(self):
        if not self.mavlink_thread.is_alive():
            self.mavlink_thread.start()

    def close(self):
        # TODO this can block forever if parameters continue to be added
        self._alive = False
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.master.close()

    def pipe(self, target):
        target.target_system = self.target_system

        # vehicle -> self -> target
        @self.forward_message
        def callback(_, msg):
            target.out_queue.put(msg.pack(target.master.mav))

        # target -> self -> vehicle
        @target.forward_message
        def callback(_, msg):
            msg = copy.copy(msg)
            target.fix_targets(msg)
            self.out_queue.put(msg.pack(self.master.mav))

        return target
