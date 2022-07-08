# DroneKit Python

![dronekit_python_logo](https://cloud.githubusercontent.com/assets/5368500/10805537/90dd4b14-7e22-11e5-9592-5925348a7df9.png)

[![PyPi published version](https://img.shields.io/pypi/v/dronekit.svg)](https://pypi.org/project/dronekit/)
[![Windows Build status](https://img.shields.io/appveyor/ci/3drobotics/dronekit-python/master.svg?label=windows)](https://ci.appveyor.com/project/3drobotics/dronekit-python/branch/master)
[![OS X Build Status](https://img.shields.io/travis/dronekit/dronekit-python/master.svg?label=os%20x)](https://travis-ci.org/dronekit/dronekit-python)
[![Linux Build Status](https://img.shields.io/circleci/project/dronekit/dronekit-python/master.svg?label=linux)](https://circleci.com/gh/dronekit/dronekit-python) <a href="https://gitter.im/dronekit/dronekit-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge"><img align="right" src="https://badges.gitter.im/Join%20Chat.svg"></img></a>

DroneKit-Python helps you create powerful apps for UAVs.


## Overview

DroneKit-Python (formerly DroneAPI-Python) contains the python language implementation of DroneKit.

The API allows developers to create Python apps that communicate with vehicles over MAVLink. It provides programmatic access to a connected vehicle's telemetry, state and parameter information, and enables both mission management and direct control over vehicle movement and operations.

The API is primarily intended for use in onboard companion computers (to support advanced use cases including computer vision, path planning, 3D modelling etc). It can also be used for ground station apps, communicating with vehicles over a higher latency RF-link. 

## Getting Started

The [Quick Start](https://dronekit-python.readthedocs.io/en/latest/guide/quick_start.html) guide explains how to set up DroneKit on each of the supported platforms (Linux, Mac OSX, Windows) and how to write a script to connect to a vehicle (real or simulated).

A basic script looks like this:

```python
from dronekit import connect

# Connect to UDP endpoint.
vehicle = connect('127.0.0.1:14550', wait_ready=True)
# Use returned Vehicle object to query device state - e.g. to get the mode:
print("Mode: %s" % vehicle.mode.name)
```

Once you've got DroneKit set up, the [guide](https://dronekit-python.readthedocs.io/en/latest/guide/index.html) explains how to perform operations like taking off and flying the vehicle. You can also try out most of the tasks by running the [examples](https://dronekit-python.readthedocs.io/en/latest/examples/index.html).

## Resources

The project documentation is available at [https://readthedocs.org/projects/dronekit-python/](https://readthedocs.org/projects/dronekit-python/). This includes [guide](https://dronekit-python.readthedocs.io/en/latest/guide/index.html), [example](https://dronekit-python.readthedocs.io/en/latest/examples/index.html) and [API Reference](https://dronekit-python.readthedocs.io/en/latest/automodule.html) material.

The example source code is hosted here on Github as sub-folders of [/dronekit-python/examples](https://github.com/dronekit/dronekit-python/tree/master/examples).

The [DroneKit Forums](http://discuss.dronekit.io) are the best place to ask for technical support on how to use the library. You can also check out our [Gitter channel](https://gitter.im/dronekit/dronekit-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) though we prefer posts on the forums where possible.

* **Documentation:** [https://dronekit-python.readthedocs.io/en/latest/about/index.html](https://dronekit-python.readthedocs.io/en/latest/about/index.html)
* **Guides:** [https://dronekit-python.readthedocs.io/en/latest/guide/index.html)
* **API Reference:** [https://dronekit-python.readthedocs.io/en/latest/automodule.html)
* **Examples:** [/dronekit-python/examples](https://github.com/dronekit/dronekit-python/tree/master/examples)
* **Forums:** [http://discuss.dronekit.io/](http://discuss.dronekit.io)
* **Gitter:** [https://gitter.im/dronekit/dronekit-python](https://gitter.im/dronekit/dronekit-python?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) though we prefer posts on the forums where possible.


## Users and contributors wanted!

We'd love your [feedback and suggestions](https://github.com/dronekit/dronekit-python/issues) about this API and are eager to evolve it to meet your needs, please feel free to create an issue to report bugs or feature requests.

If you've created some awesome software that uses this project, [let us know on the forums here](https://discuss.dronekit.io/t/notable-projects-using-dronekit/230)!

If you want to contribute, see our [Contributing](https://dronekit-python.readthedocs.io/en/latest/contributing/index.html) guidelines, we welcome all types of contributions but mostly contributions that would help us shrink our [issues list](https://github.com/dronekit/dronekit-python/issues).


## Licence

DroneKit-Python is made available under the permissive open source [Apache 2.0 License](http://python.dronekit.io/about/license.html). 


***

Copyright 2015 3D Robotics, Inc.
