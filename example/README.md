

# DroneAPI Tutorials

## Preperation (installing DroneAPI)

See the installation [instructions](documentation/install.md).

You can use DroneAPI with either a physical vehicle (pixhawk, Iris, etc...) or a simulated vehicle.  For instructions on using our simulator see this [link](http://dev.ardupilot.com/wiki/simulation-2/setting-up-sitl-using-vagrant/).

FIXME - explain that the demos build on each other, so go in sequence

## Demo 0: Hello world

This basic '[hello-world](documentation/hello-world-demo.md)' demo will show you how to connect to a vehicle and receive some basic information.

## Demo 1: Basic vehicle control

The next [demo](documentation/simple-demo-goto.mdcp ) builds on what you learned in demo zero, to actually tell the vehicle to go someplace.

## Demo 2: Drone delivery the easy way

Building on the basic vehicle control you just learned, we now [show](documentation/drone-delivery-demo.md) how to write a small web application that allows you to command a drone to fly to a particular location.

## Demo 3: Integrating the webservice

This [demonstration](documentation/flight-replay-demo.md) teaches you the basics of using the webservice and the local vehicle API to 'replay' a flight which has been uploaded to Droneshare.

## Demo 4: Follow-me (linux only)

This [demonstration](documentation/follow-me-demo.md) illustrates how to work with existing Linux services (gpsd) to add a new drone based feature.