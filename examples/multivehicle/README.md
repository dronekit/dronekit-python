These are some (hopefully short-lived) intructions on how to get multiple vehicles running in dronekit-python.  These instructions assume you are running under Linux, but with minimal modification should run on other operating systems.

Please note that these instructions will significantly change your environment.  Unless you are quite familiar with how your build environment is put together you may wish to do this in a separate stand-alone environment.

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

2. Run the _mavsource_ branch of pymavlink

  This branch introduces an object into pymavlink which filters messages to go to and come from a single system (e.g. your drone).  Without this object, the abstractions in pymavlink do not allow manipulation of multiple vehicles suitable for dronekit-python.

  ```
  ARDUPILOT_HOME=$HOME/ardupilot # e.g.
  cd $ARDUPILOT_HOME/modules/mavlink/pymavlink
  git remote add peterbarker https://github.com/peterbarker/pymavlink
  git fetch --all peterbarker
  git checkout peterbarker/mavsource
  python setup.py build install --user --force
  ```

  Note that in the above shell code we are re-using a pymavlink
  repository present in a buildable ArduPilot repository.  You can
  instead clone the pymavlink tree directly.

5. Run the multivehicle sample program:
  ```
  DRONEKIT_TOP=$HOME # e.g.
  export PYTHONPATH=$DRONEKIT_TOP/dronekit-python:$DRONEKIT_TOP/dronekit-sitl
  cd $DRONEKIT_TOP/dronekit-python/examples/multivehicle
  python multivehicle.py  --simulation-count 3 --extra-connection udpout:localhost:9432
  ```

6. Connect a GCS to port 9432

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
