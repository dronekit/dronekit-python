#!/usr/bin/env python

import time
from pymavlink import mavutil

# Clean impl of mp dependencies for droneapi

class MPFakeState:
    def __init__(self):
        self.conn = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        self.command_map = {}
        self.completions = {}

    def loop(self):
        while True:
            time.sleep(0.1)
            msg = self.conn.recv_msg()
            if msg:
                print(msg)

import droneapi.module.api as api

state = MPFakeState()
api.init(state)
state.loop()
