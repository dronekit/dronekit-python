#!/usr/bin/env python

import time
from pymavlink import mavutil

def mproxy():
    conn = mavutil.mavlink_connection('tcp:127.0.0.1:5760')

    while True:
        time.sleep(0.1)
        msg = conn.recv_msg()
        if msg:
            print(msg)

mproxy()
