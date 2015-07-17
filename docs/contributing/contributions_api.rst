.. _contributing_api:

=======================
Contributing to the API
=======================

This article provides a high level overview of how to contribute changes to the DroneKit-Python source code.

.. tip:: 

    We highly recommend that changes and ideas are `discussed with the project team 
    <https://github.com/diydrones/dronekit-python/issues>`_ before starting work! 


Submitting changes
==================

Contributors should fork the main `diydrones/dronekit-python/ <https://github.com/diydrones/dronekit-python>`_ 
repository and contribute changes back to the project master branch using pull requests

* Changes should be :ref:`tested locally <contributing-test-code>` before submission.
* Changes to the public API should be :ref:`documented <contributing-to-documentation>` (we will provide subediting support!)
* Pull requests should be as small and focussed as possible to make them easier to review.
* Pull requests should be rebased against the main project before submission to make integration easier.



.. _contributing-test-code:

Test code
=========

Test code should be used to verify new and changed functionality. Changes to DroneKit can be tested locally by rebuilding your git branch and running it locally. The links below provide information on how to set up a development environment on your development computer:

* :ref:`dronekit_development_linux`
* :ref:`dronekit_development_windows`

Running Web Client Tests
========================

Web client tests use nose. First export a DRONEAPI_KEY in the format `<id>.<key>`. The run:

.. code:: bash

    cd dronekit-python
    nosetests tests/web

Running Integrated Tests
========================

Integrated tests use the SITL environment to run DroneKit tests against a simulated copter.


.. code:: bash

    cd dronekit-python/tests
    python -um sitl

You can configure any of these environment variables to update it:

#. TEST_SPEEDUP - Speedup factor to SITL.
#. TEST_RATE - Sets framerate. (Default is 200 for copter, 50 for rover, 200 for plane.)
#. TEST_RETRY - Retry failed tests. This is useful if your testing environment performs inconsistently with the simulated copter.

You can also specify specific test names using:

.. code:: bash

    python -um sitl test_1.py test2_.py ...

Writing a new Test

You can write a new integrated test by adding a file with the naming scheme `test_XXX.py` to the `sitl` directory. In this file, functions with the prefix `test_` will be called with the `local_connect` parameter. For example:

.. code:: python

	from testlib import assert_equals

	def test_parameters(local_connect):
	    v = local_connect().get_vehicles()[0]

	    # Simple parameter checks
	    assert_equals(type(v.parameters['THR_MIN']), float)

This checks to see that the parameter object is of type float. Use assertions to test your code is consistent. Avoiding printing any data from your test.

The whole API is accessible from test files. Running `python -um sitl` will collect and run any new tests when invoked.

Running Unit Tests
==================

There are none, tim get on that.
