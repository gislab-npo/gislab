# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.require_version ">= 1.6.0"

CONFIG = Hash.new
# default GIS.lab server machine configuration file
conf = YAML.load_file('system/group_vars/all')
conf.each do |key, value|
  if not value.nil?
    CONFIG[key] = value
  end
end

# Configuration file for machine running under Vagrant provider.
# Use this file to override default GIS.lab configuration when
# using Vagrant provider.
if File.exist?('system/host_vars/gislab')
  conf = YAML.load_file('system/host_vars/gislab')
  conf.each do |key, value|
    if not value.nil?
      CONFIG[key] = value
    end
  end
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # set GIS.lab server machine name in VBox environment
  config.vm.define :gislab do |t|
  end

  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
  # or
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box
  config.vm.box = "precise-canonical"
  
  CONFIG['GISLAB_NETWORK'] = "192.168.111"
  config.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'] + ".5"
#  config.vm.synced_folder '.', '/vagrant', disabled: true

  config.ssh.forward_agent = true
  if not CONFIG['GISLAB_SSH_PRIVATE_KEY'].nil?
     config.ssh.private_key_path = [CONFIG['GISLAB_SSH_PRIVATE_KEY'], File.join("system", "insecure_ssh_key")]
  end

  config.vm.provision "ansible" do |ansible|
    ansible.verbose = "vv"
    ansible.playbook = "system/gislab.yml"
  end

  # VirtualBox provider
  config.vm.provider "virtualbox" do |vb, override|
    CONFIG['GISLAB_SERVER_MEMORY'] = 1024
    vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY']]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.customize ["modifyvm", :id, "--nictype2", "virtio"]

    if CONFIG['GISLAB_SERVER_GUI_CONSOLE'] == "yes"
      vb.gui = true
    end
  end
end
