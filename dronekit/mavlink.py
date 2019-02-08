from __future__ import print_function

import logging
import time
import socket
import errno
import sys
import os
import platform
import copy
from dronekit import APIException
from pymavlink import mavutil
from queue import Queue, Empty
from threading import Thread

if platform.system() == 'Windows':
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED


class MAVWriter(object):
    """
    Indirection layer to take messages written to MAVlink and send them all
    on the same thread.
    """

    def __init__(self, queue):
        self._logger = logging.getLogger(__name__)
        self.queue = queue

    def write(self, pkt):
        self.queue.put(pkt)

    def read(self):
        self._logger.critical('writer should not have had a read request')
        os._exit(43)


class mavudpin_multi(mavutil.mavfile):
    '''a UDP mavlink socket'''
    def __init__(self, device, baud=None, input=True, broadcast=False, source_system=255, source_component=0, use_native=mavutil.default_native):
        self._logger = logging.getLogger(__name__)
        a = device.split(':')
        if len(a) != 2:
            self._logger.critical("UDP ports must be specified as host:port")
            sys.exit(1)
        self.port = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server = input
        self.broadcast = False
        self.addresses = set()
        if input:
            self.port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.port.bind((a[0], int(a[1])))
        else:
            self.destination_addr = (a[0], int(a[1]))
            if broadcast:
                self.port.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.broadcast = True
        mavutil.set_close_on_exec(self.port.fileno())
        self.port.setblocking(False)
        mavutil.mavfile.__init__(self, self.port.fileno(), device, source_system=source_system, source_component=source_component, input=input, use_native=use_native)

    def close(self):
        self.port.close()

    def recv(self, n=None):
        try:
            try:
                data, new_addr = self.port.recvfrom(65535)
            except socket.error as e:
                if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK, errno.ECONNREFUSED]:
                    return ""
            if self.udp_server:
                self.addresses.add(new_addr)
            elif self.broadcast:
                self.addresses = {new_addr}
            return data
        except Exception:
            self._logger.exception("Exception while reading data", exc_info=True)

    def write(self, buf):
        try:
            try:
                if self.udp_server:
                    for addr in self.addresses:
                        self.port.sendto(buf, addr)
                else:
                    if len(self.addresses) and self.broadcast:
                        self.destination_addr = self.addresses[0]
                        self.broadcast = False
                        self.port.connect(self.destination_addr)
                    self.port.sendto(buf, self.destination_addr)
            except socket.error:
                pass
        except Exception:
            self._logger.exception("Exception while writing data", exc_info=True)

    def recv_msg(self):
        '''message receive routine for UDP link'''
        self.pre_message()
        s = self.recv()
        if len(s) > 0:
            if self.first_byte:
                self.auto_mavlink_version(s)

        m = self.mav.parse_char(s)
        if m is not None:
            self.post_message(m)

        return m


class MAVConnection(object):

    def stop_threads(self):
        if self.mavlink_thread_in is not None:
            self.mavlink_thread_in.join()
            self.mavlink_thread_in = None
        if self.mavlink_thread_out is not None:
            self.mavlink_thread_out.join()
            self.mavlink_thread_out = None

    def __init__(self, ip, baud=115200, target_system=0, source_system=255, source_component=0, use_native=False):
        self._logger = logging.getLogger(__name__)

        if ip.startswith("udpin:"):
            self.master = mavudpin_multi(ip[6:], input=True, baud=baud, source_system=source_system, source_component=source_component)
        else:
            self.master = mavutil.mavlink_connection(ip, baud=baud, source_system=source_system, source_component=source_component)

        # TODO get rid of "master" object as exposed,
        # keep it private, expose something smaller for dronekit
        self.out_queue = Queue()
        self.master.mav = mavutil.mavlink.MAVLink(
            MAVWriter(self.out_queue),
            srcSystem=self.master.source_system,
            srcComponent=self.master.source_component,
            use_native=use_native)

        # Monkey-patch MAVLink object for fix_targets.
        sendfn = self.master.mav.send

        def newsendfn(mavmsg, *args, **kwargs):
            self.fix_targets(mavmsg)
            return sendfn(mavmsg, *args, **kwargs)

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
            self.stop_threads()

        atexit.register(onexit)

        def mavlink_thread_out():
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                while self._alive:
                    try:
                        msg = self.out_queue.get(True, timeout=0.01)
                        self.master.write(msg)
                    except Empty:
                        continue
                    except socket.error as error:
                        # If connection reset (closed), stop polling.
                        if error.errno == ECONNABORTED:
                            raise APIException('Connection aborting during read')
                        raise
                    except Exception as e:
                        self._logger.exception('mav send error: %s' % str(e))
                        break
            except APIException as e:
                self._logger.exception("Exception in MAVLink write loop", exc_info=True)
                self._alive = False
                self.master.close()
                self._death_error = e

            except Exception as e:
                # http://bugs.python.org/issue1856
                if not self._alive:
                    pass
                else:
                    self._alive = False
                    self.master.close()
                    self._death_error = e

            # Explicitly clear out buffer so .close closes.
            self.out_queue = Queue()

        def mavlink_thread_in():
            # Huge try catch in case we see http://bugs.python.org/issue1856
            try:
                while self._alive:
                    # Loop listeners.
                    for fn in self.loop_listeners:
                        fn(self)

                    # Sleep
                    self.master.select(0.05)

                    while self._accept_input:
                        try:
                            msg = self.master.recv_msg()
                        except socket.error as error:
                            # If connection reset (closed), stop polling.
                            if error.errno == ECONNABORTED:
                                raise APIException('Connection aborting during send')
                            raise
                        except mavutil.mavlink.MAVError as e:
                            # Avoid
                            #   invalid MAVLink prefix '73'
                            #   invalid MAVLink prefix '13'
                            self._logger.debug('mav recv error: %s' % str(e))
                            msg = None
                        except Exception:
                            # Log any other unexpected exception
                            self._logger.exception('Exception while receiving message: ', exc_info=True)
                            msg = None
                        if not msg:
                            break

                        # Message listeners.
                        for fn in self.message_listeners:
                            try:
                                fn(self, msg)
                            except Exception:
                                self._logger.exception(
                                    'Exception in message handler for %s' % msg.get_type(),
                                    exc_info=True
                                )

            except APIException as e:
                self._logger.exception('Exception in MAVLink input loop')
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

        t = Thread(target=mavlink_thread_in)
        t.daemon = True
        self.mavlink_thread_in = t

        t = Thread(target=mavlink_thread_out)
        t.daemon = True
        self.mavlink_thread_out = t

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
        if not self.mavlink_thread_in.is_alive():
            self.mavlink_thread_in.start()
        if not self.mavlink_thread_out.is_alive():
            self.mavlink_thread_out.start()

    def close(self):
        # TODO this can block forever if parameters continue to be added
        self._alive = False
        while not self.out_queue.empty():
            time.sleep(0.1)
        self.stop_threads()
        self.master.close()

    def pipe(self, target):
        target.target_system = self.target_system

        # vehicle -> self -> target
        @self.forward_message
        def callback(_, msg):
            try:
                target.out_queue.put(msg.pack(target.master.mav))
            except:
                try:
                    assert len(msg.get_msgbuf()) > 0
                    target.out_queue.put(msg.get_msgbuf())
                except:
                    self._logger.exception('Could not pack this object on receive: %s' % type(msg), exc_info=True)

        # target -> self -> vehicle
        @target.forward_message
        def callback(_, msg):
            msg = copy.copy(msg)
            target.fix_targets(msg)
            try:
                self.out_queue.put(msg.pack(self.master.mav))
            except:
                try:
                    assert len(msg.get_msgbuf()) > 0
                    self.out_queue.put(msg.get_msgbuf())
                except:
                    self._logger.exception('Could not pack this object on forward: %s' % type(msg), exc_info=True)

        return target
