.. _running_examples_top:

====================
Running the Examples
====================

General instructions for running the example source code are given below (more explicit instructions may be 
provided in the documentation for each example):  

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this 
   is to clone the **dronekit-python** repository from Github. On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/droneapi-python.git

#. Navigate to the directory containing the example you want to run (for example **/dronekit-python/examples/vehicle_state/**).
#. Start MAVProxy :ref:`using the command for your connection <starting-mavproxy>`. 
   Assuming you are connecting to a simulated vehicle:

   .. code-block:: bash

       mavproxy.py --master=127.0.0.1:14550
   
   .. note::

      You should already have set up *MAVProxy* to :ref:`load DroneKit automatically <loading-dronekit>`. 
      If not, manually load the library using:

      .. code-block:: bash

          module load droneapi.module.api
	   
#. Once the *MAVProxy* console is running, start the example by entering: 

   .. code-block:: bash

       api start absolute_path_to_example/example_name.py
	   
   .. note::

       If you started MAVProxy from the example directory as suggested, you can omit 
       the full file path and just specify the example name:

       .. code-block:: bash

           api start example_name.py	   
	   

.. warning:: 

    Propellers should be removed before testing examples indoors (on real vehicles). 

