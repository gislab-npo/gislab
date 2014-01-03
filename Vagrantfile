# -*- mode: ruby -*-
# vi: set ft=ruby :


# Load GIS.lab configuration file
CONFIG = Hash.new
File.readlines("config.cfg").each do |line|
  values = line.split("=")
  CONFIG[values[0]] = values[1]
end

if File.exist?('config-user.cfg')
  File.readlines("config-user.cfg").each do |line|
    values = line.split("=")
    CONFIG[values[0]] = values[1]
  end
end


# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # add box from http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
  config.vm.box = "precise32-canonical"
  
  # VM config
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY'].strip]
    v.customize ["modifyvm", :id, "--nictype1", "virtio"]
    v.customize ["modifyvm", :id, "--nictype2", "virtio"]
#   v.gui = true
  end

  config.vm.hostname = "server.gis.lab"
  config.vm.provision "shell", path: "system/install.sh"
  config.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'].strip + ".5"

  config.vm.network :forwarded_port, guest: 111, host: 1111, auto_correct: true
  config.vm.network :forwarded_port, guest: 2049, host: 2049, auto_correct: true
  config.vm.network :forwarded_port, guest: 5432, host: 5432, auto_correct: true
end
