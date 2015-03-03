

# DroneAPI Tutorials

## Preperation (installing DroneAPI)

See the installation [instructions](documentation/install.md).

FIXME - add sitl instructions and instructions for working with a real device.

FIXME - explain that the demos build on each other, so go in sequence

## Demo 0: Hello world

This basic '[hello-world](documentation/hello-world-demo.md)' demo will show you how to connect to a vehicle and receive some basic information.

## Demo 1: Basic vehicle control

FIXME Connecting to a vehicle and having it go to a lat/lng (over all three GCS, over coprocessor or over web) (SITL preferred, but include instructions for real hardware)  For safety validate the lat/lng is less than 100m of the HOME loc.

## Demo 2: Drone delivery the easy way

FIXME Add basic web screen for drone-delivery (let user click on some _easy_ web map) to find the lat/lng.  Include live map update of vehicle position and if user clicks on map, go to that position and drop present (after confirming with user). Main subtasks:
 map integration
 web page goo
 talking to vehicle

## Demo 3: Integrating the webservice

FIXME Replay any droneshare mission (watch time advance set guide wpts to try and stay on the same tracklog)

## Demo 4: Follow-me (linux only)

This [demonstration](documentation/follow-me-demo.md) illustrates how to work with existing Linux services (gpsd) to add a new drone based feature.