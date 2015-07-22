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

Test code should be used to verify new and changed functionality. The links below provide information on how to set up a development environment on your development computer. Changes to DroneKit can then be tested locally. 

* :ref:`dronekit_development_linux`
* :ref:`dronekit_development_windows`

--------------
Test Structure
--------------

There are three test suites in DroneKit Python.

* ``tests/unit`` — **Unit tests** verify all code paths of the API. 
* ``tests/sitl`` — **Integration tests** verify real-world code, examples, and documentation as they would perform in a real environment.
* ``tests/web`` — **Web client** tests specifically verify the Python library's capability to talk to `DroneKit Cloud <http://cloud.dronekit.io>`_.

Several of these test suites use `nose <https://nose.readthedocs.org/en/latest/>`_, a Python library for writing test scripts and a command line tool for running these. When setting up your dev environment, all test dependencies will have been installed (via requirements.txt).

Unit Tests
^^^^^^^^^^^

Unit tests use ``nosetests``. On any OS, type this in the command line to run, then see a summary of, all unit tests:

.. code:: bash

    cd dronekit-python
    nosetests tests/unit

For unit tests, `mock <https://docs.python.org/dev/library/unittest.mock.html>`_ is used to simulate objects and APIs and ensure correct results.

Writing a new Test
""""""""""""""""""

Good unit tests should:

#. Accompany all new features that are written.
#. Verify all code paths that code can take.
#. Be concise and straightforward.

Create any file named `test_XXX.py` in the tests/unit folder to add it as a test. Feel free to copy from existing tests to get started. When `nosetests` is run, it will add your new test to its summary.

Integrated Tests
^^^^^^^^^^^^^^^^

Integrated tests use a custom test runner that is similar to ``nosetests``. On any OS, type this in the command line to run, then see a summary of, all integrated tests:

.. code:: bash

    cd dronekit-python
    python -um tests.sitl

Integrated tests use the SITL environment to run DroneKit tests against a simulated copter. Because these tests emulate a copter in real-time, you can set several environment variables to tweak the environment code is run in:

#. ``TEST_SPEEDUP`` - Speedup factor to SITL. Default is ``TEST_SPEEDUP=1``. You can increase this factor to speed up how long your tests take to run.
#. ``TEST_RATE`` - Sets framerate. Default is ``TEST_RATE=200`` for copter, 50 for rover, 50 for plane.
#. ``TEST_RETRY`` - Retry failed tests. Default is ``TEST_RETRY=1``. This is useful if your testing environment generates inconsistent success rates because of timing.

You can choose to test specific files by passing them as arguments:

.. code:: bash

    python -um tests.sitl test_1.py test2_.py ...

Writing a new Test
""""""""""""""""""

Integration tests should be written or improved whenever:

#. New functionality has been added to encapsulate or abstract older methods of interacting with the API.
#. Example code or documentation has been added.
#. A feature could not be tested by unit tests alone (e.g. timing issues, mode changing, etc.)

You can write a new integrated test by adding a file with the naming scheme ``test_XXX.py`` to the ``tests/sitl`` directory. In this file, functions with the prefix ``test_`` will be called with the `local_connect` parameter. For example:

.. code:: python

    from testlib import assert_equals

    def test_parameters(local_connect):
        v = local_connect().get_vehicles()[0]

        # Simple parameter checks
        assert_equals(type(v.parameters['THR_MIN']), float)

This checks to see that the parameter object is of type float. Use assertions to test your code is consistent. Avoiding printing any data from your test.

Web Client Tests
^^^^^^^^^^^^^^^^

Web client tests use ``nosetests``. To run these, you will need to sign up for API keys from `cloud.dronekit.io <https://cloud.dronekit.io/>`_. With these, you can export to your enviroment a variable called DRONEAPI_KEY in the format `<id>.<key>`:

.. code:: bash

    export DRONEAPI_KEY=<id>.<key>   # works on OS X and Linux
    set DRONEAPI_KEY=<id>.<key>      # works on Windows cmd.exe
    $env:DRONEAPI_KEY="<id>.<key>"   # works on Windows Powershell

On any OS, type this in the command line to run, then see a summary of, all unit tests: 

.. code:: bash

    cd dronekit-python
    nosetests tests/web
