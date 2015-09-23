.. _running_examples_top:

====================
Running the Examples
====================

General instructions for running the `example source code <https://github.com/dronekit/dronekit-python/tree/master/examples>`_ are given below.

.. tip::

    More explicit instructions may be provided within the documentation for each example, and on the command line using the ``-h`` (help) parameter.

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this 
   is to clone the **dronekit-python** repository from Github. On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/dronekit-python.git

   
   
#. Navigate to the example you wish to run (or specify the full path in the next step). The examples are all stored in 
   subdirectories of **dronekit-python\\examples\\**. 
   
   To run the :ref:`vehicle_state <example-vehicle-state>` example, you would navigate as shown:

   .. code-block:: bash

       cd dronekit-python\examples\vehicle_state\


#. Start the example, passing the :ref:`connection string <get_started_connect_string>` you wish to use in the ``--connect`` parameter:

   .. code-block:: bash

       python vehicle_state.py --connect 127.0.0.1:14550

   .. note::
   
       The examples all use the ``--connect`` parameter to pass the :ref:`connection string <get_started_connect_string>` into the script. 
       The command above would be used to connect to :ref:`SITL <sitl_setup>` running on the local machine via UDP port 14550.
          

.. warning:: 

    Propellers should be removed before testing examples indoors (on real vehicles). 
