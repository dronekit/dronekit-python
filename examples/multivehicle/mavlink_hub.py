from __future__ import print_function

from pymavlink import mavutil
import time
import threading

class Connection():
    def __init__(self, addr):
        self.addr = addr
        self._active = False
        self.last_packet_received = 0
        self.last_connection_attempt = 0

    def open(self):
        try:
            print("Opening connection to %s" % (self.addr,))
            self.mav = mavutil.mavlink_connection(self.addr)
            self._active = True
            self.last_packet_received = time.time() # lie

        except Exception as e:
            print("Connection to (%s) failed: %s" % (self.addr, str(e)))

    def close(self):
        self.mav.close()
        self._active = False

    def active(self):
        return self._active

class MAVLinkHub():
    def __init__(self, addrs):
        self.addrs = addrs
        self.conns = []
        self.connection_maintenance_target_should_live = True
        self.inactivity_timeout = 10
        self.reconnect_interval = 5

    def maintain_connections(self):
        now = time.time()
        for conn in self.conns:
            if not conn.active():
                continue
            if now - conn.last_packet_received > self.inactivity_timeout:
                print("Connection (%s) timed out" % (conn.addr,))
                conn.close()
        for conn in self.conns:
            if not conn.active():
                if now - conn.last_connection_attempt > self.reconnect_interval:
                    conn.last_connection_attempt = now
                    conn.open()
#            else:
#                print("Connection %s OK" % (conn.addr))
        time.sleep(0.1)

    def create_connections(self):
        for addr in self.addrs:
            print("Creating connection (%s)" % addr)
            self.conns.append(Connection(addr))

    def handle_messages(self):
        now = time.time()
        packet_received = False
        for conn in self.conns:
            if not conn.active():
                continue
            m = None
            try:
                m = conn.mav.recv_msg()
            except Exception as e:
                print("Exception receiving message on addr(%s): %s" % (str(conn.addr),str(e)))
                conn.close()

            if m is not None:
                conn.last_packet_received = now
                packet_received = True
#               print("Received message (%s) on connection %s from src=(%d/%d)" % (str(m), conn.addr, m.get_srcSystem(), m.get_srcComponent(),))
                for j in self.conns:
                    if not j.active():
                        continue
                    if j.addr == conn.addr:
                        continue
#                    print("  Resending message on connection %s" % (j.addr,))
                    j.mav.write(m.get_msgbuf())
        if not packet_received:
            time.sleep(0.01)

    def init(self):
        self.create_connections()
        self.create_connection_maintenance_thread()
        
    def loop(self):
        self.handle_messages()

    def create_connection_maintenance_thread(self):
        '''create and start helper threads and the like'''
        def connection_maintenance_target():
            while self.connection_maintenance_target_should_live:
                self.maintain_connections()
                time.sleep(0.1)
        connection_maintenance_thread = threading.Thread(target=connection_maintenance_target)
        connection_maintenance_thread.start()

    def run(self):
        self.init()

#        print("Entering main loop")
        while True:
            self.loop()

if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser("mavlink_hub.py [options]")
    (opts, args) = parser.parse_args()

    hub = MAVLinkHub(args)
    if len(args) == 0:
        print("Insufficient arguments")
        sys.exit(1)
    hub.run()
