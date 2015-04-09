============
Contributing
============

DroneKit is an open-source project. We welcome any contribution that will improve the API — adding new features and making it easier to use. 


Getting started
================

The dronekit-python project is `hosted on Github here <https://github.com/diydrones/dronekit-python/>`_. This where you get the source code, and is the best place to raise `bug reports and enhancement suggestions <https://github.com/diydrones/dronekit-python/issues>`_.

.. tip:: Before starting new work, first create an issue in Github so it can be tracked and discussed! 

In addition to creating defect reports, a good starting point is to work on the `open issues <https://github.com/diydrones/dronekit-python/issues>`_ on Github. In particular, :ref:`documentation issues <contributing-to-documentation>` can be resolved without a deep knowledge of the code, and will help you learn more about the project.


How to submit changes
=====================

Contributors should fork the main project Github repository and contribute changes back to the project using pull requests:

* Ideas should be discussed with the project team first (using an issue) 
* Pull requests should be as small and focussed as possible to make them easier to review
* Rebase your code against the main project before submission to make integration easier



.. _contributing-to-documentation:

Contributing to the API documentation
=====================================

One of the best ways that you can help is by improving this documentation.  

The documentation source files are `stored in Github <https://github.com/diydrones/dronekit-python/tree/master/docs>`_. The content is written in plain-text files (file-extension :file:`.rst`) using `reStructuredText <http://sphinx-doc.org/rest.html>`_ markup, and is compiled into HTML using the `Sphinx Documentation Generator <http://sphinx-doc.org/index.html>`_. As with any other contributions to this project, you should fork the main project Github repository and contribute changes back to the project using pull requests.

We've made it very easy to get started by providing a `Vagrant <https://www.vagrantup.com/>`_ based setup for :program:`Sphinx`. Using :program:`Vagrant` you can work with source files on your host machine using a familiar :program:`git` client and text editor, and then invoke :program:`Sphinx` in the :program:`Vagrant` VM to compile the source to HTML.

The instructions below explain how to get the documentation source, and build it using our Vagrant VM:
	
* Install the Vagrant pre-conditions:

  * `Download and install VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.
  * `Download and install Vagrant for your platform <https://www.vagrantup.com/downloads.html>`_ (Windows, OS-X and Linux are supported).
  
* `Fork the official dronekit-python repo <https://github.com/diydrones/dronekit-python#fork-destination-box>`_
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

	
* After making changes, follow the normal process to submit them to the project (i.e.commit and push them to your fork on Github, and then create a pull request on Github to the project repository).

	
	
		
		




