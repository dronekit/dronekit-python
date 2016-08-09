These are some (hopefully short-lived) intructions on how to get this avoidance example running in dronekit-python.  These instructions assume you are running under Linux, but with minimal modification should run on other operating systems.

Please note that these instructions will significantly change your environment.  Unless you are quite familiar with how your build environment is put together you may wish to do this in a separate stand-alone environment.

1. Run peterbarker's _source-system-filtering branch_ of dronekit-python

  Given that this README file exists within that branch, this should not be too much of a problem.

  The branch can be cloned from ssh://git@github.com/peterbarker/dronekit-python.git
  ```
  DRONEKIT_TOP=$HOME # e.g.
  cd $DRONEKIT_TOP/dronekit-python
  got remote add peterbarker ssh://git@github.com/peterbarker/dronekit-python.git
  git fetch peterbarker
  git checkout peterbarker/source-system-filtering
  ```

2. Run version of mavlink which contains source system filtering:

  ```
  ARDUPILOT_HOME=$HOME/ardupilot # e.g.
  cd $ARDUPILOT_HOME/modules/mavlink
  git remote add peterbarker https://github.com/peterbarker/mavlink
  git fetch --all peterbarker
  git checkout peterbarker/mavsystem-object
  cd $ARDUPILOT_HOME/modules/mavlink/pymavlink
  python setup.py build install --user --force
  ```
  

3. Run peterbarker's avoidance MAVProxy branch

  ```
  MAVPROXY_HOME=$HOME/ardupilot # e.g.
  cd $MAVPROXY_HOME
  git remote add peterbarker https://github.com/peterbarker/MAVProxy
  git fetch peterbarker
  git checkout avoidance
  python seutp.setup.py build install --user --force
  ```

4. Run the _multivehicle-wip_ branch of dronekit-sitl

  This branch allows the user to specify a --defaults option to the SITL instance, allowing modern ArduPilots to run.  It also adds diagnostic options.

  ```
  DRONEKIT_TOP=$HOME # e.g.
  git clone https://github.com/dronekit/dronekit-sitl
  cd $DRONEKIT_TOP/dronekit-sitl
  git checkout multivehicle-wip
  ```
  
5. Connect a GCS to port 3456

  This varies by GCS.  With *MAVProxy* you might run this:
  ```
  mavproxy.py --master udpin:localhost:3456
  module load avoidance
  ```

  With *GQGroundControl* you might try this:
    ```
    - run qgroundcontrol
    - Hamburger -> Comm Links
    - Add (near the bottom of the screen)
     - Type: UDP
     - Listening port 3456
    ```

6. Run the avoidance sample program:
  ```
  DRONEKIT_TOP=$HOME # e.g.
  ARDUPILOT_HOME=$HOME/ardupilot
  export PYTHONPATH=$DRONEKIT_TOP/dronekit-python:$DRONEKIT_TOP/dronekit-sitl
  cd $DRONEKIT_TOP/dronekit-python/examples/avoidance
  python avoidance.py --binary $ARDUPILOT_HOME/build/sitl-debug/bin/arducopter-quad --resolution=PERPENDICULAR --defaults=$ARDUPILOT_HOME/Tools/autotest/copter_params.parm --extra-connection=udpout:localhost:3456

  ```
7. What you should see:
 - two quadcopters should both enter guided mode
 - both should rise to 5m
 - one of the copters will start to head north
 - a second quadcopter will start to head north-north-west
 - the second quadcopter will approach too closely to the first quadcopter and take a perpendicular course to the first quadcopter

