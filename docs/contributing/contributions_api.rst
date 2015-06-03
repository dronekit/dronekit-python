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

Test code should be used to verify new and changed functionality. Changes to DroneKit can be tested locally by 
rebuilding your git branch and running it against SITL. The links below provide information on how 
to set up a development environment on your development computer:

* :ref:`dronekit_development_linux`
* :ref:`dronekit_development_vagrant` (Windows and MacOSX)

.. note:: At time of writing (June 2015) we do not yet have formal acceptance tests (unit tests, system tests).

We recommend that you provide your test script as a gist, and run any the 
:ref:`DroneKit-Python Examples <example-toc>` that are relevant.
 
For example, the addition of a new API item for retrieving a vehicle attribute would need test code for 
getting, setting (if applicable) and printing the attribute. An easy way to create this would be to 
update and run :ref:`example-vehicle-state`.



