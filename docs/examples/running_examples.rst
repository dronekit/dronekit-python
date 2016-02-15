.. _running_examples_top:

====================
Running the Examples
====================

General instructions for running the `example source code <https://github.com/dronekit/dronekit-python/tree/master/examples>`_ are given below. More explicit instructions are provided within the documentation for each example (and within the examples themselves by passing the ``-h`` (help) command line argument).

.. tip::

    The examples all launch the :ref:`dronekit-sitl <dronekit_sitl>` simulator and connect to it by default. The ``--connect`` argument is used to instead specify the :ref:`connection string <get_started_connect_string>` for a target vehicle or an externally managed SITL instance.
    
To run the examples:

#. :ref:`Install DroneKit-Python <installing_dronekit>` if you have not already done so! Install :ref:`dronekit-sitl <dronekit_sitl>` if you want to test against simulated vehicles.

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this 
   is to clone the **dronekit-python** repository from Github. 
   
   On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/dronekit-python.git

   
   
#. Navigate to the example you wish to run (or specify the full path in the next step). The examples are all stored in 
   subdirectories of **dronekit-python/examples/**. 
   
   For example, to run the :ref:`vehicle_state <example-vehicle-state>` example, you would navigate as shown:

   .. code-block:: bash

       cd dronekit-python/examples/vehicle_state/


#. Start the example as shown:

   * To connect to a simulator started/managed by the script:
   
     .. code-block:: bash

         python vehicle_state.py

   * To connect to a specific vehicle, pass its :ref:`connection string <get_started_connect_string>` via the ``connect`` argument. 
     For example, to run the example on Solo you would use the following command:
   
     .. code-block:: bash

         python vehicle_state.py --connect udpin:0.0.0.0:14550


.. warning:: 

    Propellers should be removed before testing examples indoors (on real vehicles). 
