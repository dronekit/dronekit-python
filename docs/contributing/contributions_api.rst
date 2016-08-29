.. _contributing_api:

=======================
Contributing to the API
=======================

This article provides a high level overview of how to contribute changes to the DroneKit-Python source code.

.. tip::

    We highly recommend that changes and ideas are `discussed with the project team
    <https://github.com/dronekit/dronekit-python/issues>`_ before starting work!


Submitting changes
==================

Contributors should fork the main `dronekit/dronekit-python/ <https://github.com/dronekit/dronekit-python>`_
repository and contribute changes back to the project master branch using pull requests

* Changes should be :ref:`tested locally <contributing-test-code>` before submission.
* Changes to the public API should be :ref:`documented <contributing-to-documentation>` (we will provide subediting support!)
* Pull requests should be as small and focussed as possible to make them easier to review.
* Pull requests should be rebased against the main project before submission to make integration easier.



.. _contributing-test-code:

Test code
=========

There are three test suites in DroneKit-Python:

* **Unit tests** (:file:`tests/unit`) — verify all code paths of the API.
* **Integration tests** (:file:`tests/sitl`) — verify real-world code, examples, and documentation as they would perform in a real environment.

Test code should be used to verify new and changed functionality. New tests should:

#. Verify all code paths that code can take.
#. Be concise and straightforward.
#. Be documented.


Setting up local testing
------------------------

Follow the links below to set up a development environment on your Linux or Windows computer.

* :ref:`dronekit_development_linux`
* :ref:`dronekit_development_windows`

The tests require additional pip modules, including `nose <https://nose.readthedocs.org/en/latest/>`_, a
Python library and tool for writing and running test scripts. These can be installed separately using either of the commands below:

.. code:: bash

    # Install just the additional requirements for tests
    pip install requests nose mock

    # (or) Install all requirements for dronekit, tests, and building documentation
    pip install -r requirements.txt

For several tests, you may be required to set an **environment variable**. In your command line, you can set the name of a variable to equal a value using the following invocation, depending on your OS:

.. code:: bash

    export NAME=VALUE      # works on OS X and Linux
    set NAME=VALUE         # works on Windows cmd.exe
    $env:NAME = "VALUE"    # works on Windows Powershell

Unit tests
----------

All new features should be created with accompanying unit tests.

DroneKit-Python unit tests are based on the `nose <https://nose.readthedocs.org/en/latest/>`_ test framework,
and use `mock <https://docs.python.org/dev/library/unittest.mock.html>`_ to simulate objects and APIs and
ensure correct results.

To run the tests and display a summary of the results (on any OS),
navigate to the **dronekit-python** folder and enter the following
command on a terminal/prompt:

.. code:: bash

    nosetests dronekit.test.unit




Writing a new unit test
^^^^^^^^^^^^^^^^^^^^^^^

Create any file named :file:`test_XXX.py` in the :file:`tests/unit` folder to add it as a test.
Feel free to copy from existing tests to get started. When *nosetests* is run, it will add your new test to its summary.

Tests names should be named based on their associated Github issue (for example,
``test_12.py`` for `issue #12 <https://github.com/dronekit/dronekit-python/issues/12>`_)
or describe the functionality covered (for example, ``test_waypoints.py``
for a unit test for the waypoints API).

Use assertions to test your code is consistent. You can use the built-in Python ``assert`` macro as well as ``assert_equals`` and ``assert_not_equals``
from the ``notestools`` module:

.. note::

    Avoiding printing any data from your test!

.. code:: python

    from nose.tools import assert_equals, assert_not_equals

    def test_this(the_number_two):
        assert the_number_two > 0, '2 should be greater than zero!'
        assert_equals(the_number_two, 2, '2 should equal two!')
        assert_not_equals(the_number_two, 1, '2 should equal one!')

Please add documentation to each test function describing what behavior it verifies.


Integration tests
-----------------

Integrated tests use a custom test runner that is similar to *nosetests*. On any OS, enter the following command on a terminal/prompt to run all the integrated tests (and display summary results):

.. code:: bash

    cd dronekit-python
    nosetests dronekit.test.sitl

You can choose to run a specific tests. The example below shows how to run
**\dronekit-python\dronekit\test\sitl\test_12.py**.

.. code:: bash

    nosetests dronekit.test.sitl.test_12


Configuring the test environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integrated tests use the SITL environment to run DroneKit tests against a simulated Copter. Because these tests emulate Copter in real-time, you can set several environment variables to tweak the environment that code is run in:

#. ``TEST_SPEEDUP`` - Speedup factor to SITL. Default is ``TEST_SPEEDUP=1``. You can increase this factor to speed up how long your tests take to run.
#. ``TEST_RATE`` - Sets framerate. Default is ``TEST_RATE=200`` for copter, 50 for rover, 50 for plane.
#. ``TEST_RETRY`` - Retry failed tests. Default is ``TEST_RETRY=1``. This is useful if your testing environment generates inconsistent success rates because of timing.



Writing a new integration test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integration tests should be written or improved whenever:

#. New functionality has been added to encapsulate or abstract older methods of interacting with the API.
#. Example code or documentation has been added.
#. A feature could not be tested by unit tests alone (e.g. timing issues, mode changing, etc.)

You can write a new integrated test by adding (or copying) a file with the naming scheme :file:`test_XXX.py` to the :file:`tests/sitl` directory.

Tests names should be named based on their associated Github issue (for example,
``test_12.py`` for `issue #12 <https://github.com/dronekit/dronekit-python/issues/12>`_)
or describe the functionality covered (for example, ``test_waypoints.py``
for an integration test for the waypoints API).

Tests should minimally use the imports shown below and decorate test functions with ``@with_sitl``
(this sets up the test and passes in a connection string for SITL).

.. code:: python

    from dronekit import connect
    from dronekit.test import with_sitl
    from nose.tools import assert_equals, assert_not_equals

    @with_sitl
    def test_something(connpath):
        vehicle = connect(connpath)

        # Test using assert, assert_equals and assert_not_equals
        ...

        vehicle.close()


Use assertions to test your code is consistent. You can use the built-in Python ``assert`` macro as well as ``assert_equals`` and ``assert_not_equals``
from the ``testlib`` module:

.. note::

    Avoiding printing any data from your test!



.. code:: python

    from testlib import assert_equals

    def test_this(the_number_two):
        assert the_number_two > 0, '2 should be greater than zero!'
        assert_equals(the_number_two, 2, '2 should equal two!'

Please add documentation to each test function describing what behavior it verifies.
