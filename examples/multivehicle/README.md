These are some (hopefully short-lived) intructions on how to get multiple vehicles running in dronekit-python.  These instructions assume you are running under Linux, but with minimal modification should run on other operating systems.

1. Run peterbarker's _source-system-filtering branch_ of dronekit-python

  Given that this README file exists within that branch, this should not be too much of a problem.

  The branch exists in this fork of dronekit-python: can be cloned from ssh://git@github.com/peterbarker/dronekit-python.git
  ```
  DRONEKIT_TOP=$HOME # e.g.
  cd $DRONEKIT_TOP/dronekit-python
  git remote add peterbarker ssh://git@github.com/peterbarker/dronekit-python.git
  git fetch peterbarker
  git checkout peterbarker/source-system-filtering
  ```

2. Run the _mavsystem-object_ branch of mavlink

  This branch introduces an object into pymavlink which filters messages to go to and come from a single system (e.g. your drone).  Without this object, the abstractions in pymavlink do not allow manipulation of multiple vehicles suitable for dronekit-python.

  To run this branch, one would typically "git clone" it, then install it locally with:

  ```
  DRONEKIT_TOP=$HOME # e.g.
  cd $DRONEKIT_TOP/mavlink
  git remote add peterbarker ssh://git@github.com/peterbarker/dronekit-python.git
  git fetch peterbarker
  git checkout mavsystem-object
  cd pymavlink
  python setup.py build install --user --force
  ```

  You want to be comfortable doing this; if this is not how you typically use pymavlink then you may have trouble reverting to your normal configuration.

3. Run the _peterbarker-multivehicle-wip_ branch of dronekit-sitl

  This branch contains various changes:
   - use an ArduPilot you compile yourself rather than a pre-canned one
   - attach GDB to the ArduPilot instances
   - more easily support more than one ArduPilot instance
   - emit output from the ArduPilot instance

  ```
  DRONEKIT_TOP=$HOME # e.g.
  cd $DRONEKIT_TOP/dronekit-sitl
  git checkout peterbarker-multivehicle-wip
  ```
  
4. Run the multivehicle sample program:
  ```
  DRONEKIT_TOP=$HOME # e.g.
  export PYTHONPATH=$DRONEKIT_TOP/dronekit-python:$DRONEKIT_TOP/dronekit-sitl
  cd $DRONEKIT_TOP/dronekit-python/examples/multivehicle
  python multivehicle.py  --simulation-count 3 --extra-connection udpout:localhost:9432
  ```

5. Connect a GCS to port 9432

  This varies by GCS.  With *MAVProxy* you might run this:
  ```
  mavproxy.py --master udpin:localhost:9432
  ```

  With *GQGroundControl* you might try this:
    ```
    - run qgroundcontrol
    - Hamburger -> Comm Links
    - Add (near the bottom of the screen)
     - Type: UDP
     - Listening port 9432
     - You should see both vehicles appear at this point
    ```
