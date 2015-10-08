from dronekit import local_connect

def demo(local_connect):
    # This example shows how to use DroneKit-Python to get and set vehicle state, parameter and channel-override information. 
    # It also demonstrates how to observe vehicle attribute (state) changes. 
    # 
    # Usage:
    # * mavproxy.py
    # * module load api
    # * api start vehicle-state.py
    #
    from dronekit.lib import VehicleMode
    from pymavlink import mavutil
    import time

    # First get an instance of the API endpoint
    api = local_connect()
    # Get the connected vehicle (currently only one vehicle can be returned).
    v = api.get_vehicles()[0]

    # Get all vehicle attributes (state)
    print "\nGet all vehicle attribute values:"
    print " Location: %s" % v.location
    print " Attitude: %s" % v.attitude
    print " Velocity: %s" % v.velocity
    print " GPS: %s" % v.gps_0
    print " Groundspeed: %s" % v.groundspeed
    print " Airspeed: %s" % v.airspeed
    print " Mount status: %s" % v.mount_status
    print " Battery: %s" % v.battery
    print " Mode: %s" % v.mode.name    # settable
    print " Armed: %s" % v.armed    # settable

    # Set vehicle mode and armed attributes (the only settable attributes)
    print "Set Vehicle.mode=GUIDED (currently: %s)" % v.mode.name 
    v.mode = VehicleMode("GUIDED")
    v.flush()  # Flush to guarantee that previous writes to the vehicle have taken place
    while not v.mode.name=='GUIDED' and not api.exit:  #Wait until mode has changed
        print " Waiting for mode change ..."
        time.sleep(1)

    print "Set Vehicle.armed=True (currently: %s)" % v.armed 
    v.armed = True
    v.flush()
    while not v.armed and not api.exit:
        print " Waiting for arming..."
        time.sleep(1)


    # Show how to add and remove and attribute observer callbacks (using mode as example) 
    def mode_callback(attribute):
        print " CALLBACK: Mode changed to: ", v.mode.name

    print "\nAdd mode attribute observer for Vehicle.mode" 
    v.add_attribute_observer('mode', mode_callback) 

    print " Set mode=STABILIZE (currently: %s)" % v.mode.name 
    v.mode = VehicleMode("STABILIZE")
    v.flush()

    print " Wait 2s so callback invoked before observer removed"
    time.sleep(2)

    # Remove observer - specifying the attribute and previously registered callback function
    v.remove_attribute_observer('mode', mode_callback)  


    # #  Get Vehicle Home location ((0 index in Vehicle.commands)
    # print "\nGet home location" 
    # cmds = v.commands
    # cmds.download()
    # cmds.wait_valid()
    # print " Home WP: %s" % cmds[0]


    #  Get/Set Vehicle Parameters
    print "\nRead vehicle param 'THR_MIN': %s" % v.parameters['THR_MIN']
    print "Write vehicle param 'THR_MIN' : 10"
    v.parameters['THR_MIN']=10
    v.flush()
    print "Read new value of param 'THR_MIN': %s" % v.parameters['THR_MIN']


    # # Overriding an RC channel
    # # NOTE: CHANNEL OVERRIDES may be useful for simulating user input and when implementing certain types of joystick control. 
    # #DO NOT use unless there is no other choice (there almost always is!)
    # print "\nOverriding RC channels for roll and yaw"
    # v.channel_override = { "1" : 900, "4" : 1000 }
    # v.flush()
    # print " Current overrides are:", v.channel_override
    # print " Channel default values:", v.channel_readback  # All channel values before override

    # # Cancel override by setting channels to 0
    # print " Cancelling override"
    # v.channel_override = { "1" : 0, "4" : 0 }
    # v.flush()


    ## Reset variables to sensible values.
    print "\nReset vehicle atributes/parameters and exit"
    v.mode = VehicleMode("STABILIZE")
    v.armed = False
    v.parameters['THR_MIN']=130
    v.flush()

demo(local_connect)
