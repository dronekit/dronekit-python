# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    config.vm.box = "ubuntu/trusty64"

    config.vm.provision "shell", inline: <<-SHELL
        apt-get -y update
        echo "[DroneKit]: Installing build essentials"
        apt-get -y install build-essential
        echo "[DroneKit]: Installing Python Devel"
        apt-get -y install python-dev
        echo "[DroneKit]: Installing pip ..."
        apt-get -y install python-pip
        easy_install -U pip
        echo "[DroneKit]: Installing Sphinx ... "
        pip install sphinx
        cd /vagrant
        echo "[DroneKit]: Installing DroneKit-Python requirements.txt ... "
        pip install -r requirements.txt
        echo "[DroneKit]: Building docs "
        cd docs/
        make html
    SHELL
end
