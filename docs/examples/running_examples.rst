.. _running_examples_top:

====================
Running the Examples
====================

General instructions for running the example source code are given below (more explicit instructions may be 
provided in the documentation for each example):  

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this 
   is to clone the **dronekit-python** repository from Github. On the command prompt enter:

   .. code-block:: bash

       git clone http://github.com/dronekit/dronekit-python.git

   .. tip:: 

       The :ref:`Windows Installation <get_started_install_dk_windows>` copies the example code here: 
       :file:`C:\\Program Files (x86)\\MAVProxy\\examples\\`.

#. Start MAVProxy and :ref:`connect to the vehicle <starting-mavproxy>`. For example:

   * To connect to a simulated vehicle when starting *MAVProxy* (from the command line):

     .. code-block:: bash

         mavproxy.py --master=127.0.0.1:14550
   
   * To connect to a simulated vehicle after starting MAVProxy (for example, on Windows):

     .. code-block:: bash

         link add 127.0.0.1:14550

#. You should already have set up *MAVProxy* to :ref:`load DroneKit automatically <loading-dronekit>`. 
   If not, manually load the library using:

   .. code-block:: bash

       module load dronekit.module.api
	   
#. Once the *MAVProxy* console is running, start the example by entering: 

   .. code-block:: bash

       api start absolute_path_to_example/example_name.py
	   
   .. tip::

       If you start *MAVProxy* from the same directory as the target script you can omit 
       the full file path:

       .. code-block:: bash

           api start example_name.py	   
	   

.. warning:: 

    Propellers should be removed before testing examples indoors (on real vehicles). 

