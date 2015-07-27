.. _contributing-to-documentation:

=================================
Contributing to the Documentation
=================================

One of the best ways that you can help is by improving this documentation.  Here we explain
the documentation system, how to build the documents locally, and how to submit your changes.


Documentation system overview
=============================

The documentation source files are `stored in Github <https://github.com/dronekit/dronekit-python/tree/master/docs>`_. 
The content is written in plain-text files (file-extension :file:`.rst`) using 
`reStructuredText <http://sphinx-doc.org/rest.html>`_ markup, and is compiled into HTML using the 
`Sphinx Documentation Generator <http://sphinx-doc.org/index.html>`_. 

Submitting changes
==================

The process and requirements for submitting changes to the documentation are **the same** as when 
:ref:`contributing to the source code <contributing_api>`. 

As when submitting source code you should fork the main project Github repository and 
contribute changes back to the project using pull requests. The changes should be tested
locally (by :ref:`building the docs <contributing_building_docs>`) before being submitted.

See :ref:`contributing_api` for more information. 

.. _contributing_building_docs:

Building the docs
=================

We've made it very easy to get started by providing a `Vagrant <https://www.vagrantup.com/>`_ based setup for :program:`Sphinx`. Using :program:`Vagrant` you can work with source files on your host machine using a familiar :program:`git` client and text editor, and then invoke :program:`Sphinx` in the :program:`Vagrant` VM to compile the source to HTML.

The instructions below explain how to get the documentation source, and build it using our Vagrant VM:
	
* Install the Vagrant pre-conditions:

  * `Download and install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
  * `Download and install Vagrant for your platform <https://www.vagrantup.com/downloads.html>`_ (Windows, OS-X and Linux are supported).
  
* `Fork the official dronekit-python repo <https://github.com/dronekit/dronekit-python#fork-destination-box>`_
* Clone your fork of the Github repository anywhere on the host PC: ::

    git clone https://github.com/YOUR-REPOSITORY/dronekit-python.git
	
* Navigate to the root of *dronekit-python* and start the Vagrant VM:
  ::
  
	cd /your-path-to-clone/dronekit-python/
	vagrant up

  .. note:: This may take a long time to complete the first time it is run  — Vagrant needs to download the virtual machine and then set up Sphinx.
	
* When the VM is running, you can build the source by entering the following command in the prompt: 
  ::

	vagrant ssh -c "cd /vagrant/docs && make html"
		
  The files will be built by :program:`Sphinx`, and will appear on the host system in :file:`<clone-path>/dronekit-python/docs/\_build/html/`. To preview, simply open them in a Web browser.
	
  .. note:: 

	The ``vagrant ssh -c "cd /vagrant/docs && make html"`` command starts (and closes) an SSH session with the VM. If you plan on building the source a number of times it is much faster to keep the session open: 
		
	::

		vagrant ssh        # Open an SSH session with the Vagrant VM
		cd /vagrant/docs   # Navigate to the docs root (contains Sphinx configuration files)
		make html          # Build the HTML
		...                # Repeat "make html" as many time as needed
		make html          
		exit               # Close the SSH session.

			
	
* When you are finished you can suspend the VM. Next time you need to build more HTML simply restart it (this is a fast operation):
  ::
  
	vagrant suspend   #Suspend the VM
	vagrant resume    #Restart the VM
	vagrant ssh -c "cd /vagrant/docs && make html"   #Build files when needed.


Style guide
===========

.. tip:: 

    This guide is evolving. The most important guidance we can give is 
    to *copy the existing style of reference, guide and example material*!


#. Use US English for spelling.

#. Use emphasis sparingly (italic, bold, underline). 

#. Use `Sphinx semantic markup <http://sphinx-doc.org/markup/inline.html#other-semantic-markup>`_ to mark up *types* of text (key-presses, file names etc.)

#. Use double backticks (``) around ``inline code`` items.