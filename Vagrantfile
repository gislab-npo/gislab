# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'

VAGRANTFILE_API_VERSION = "2"
Vagrant.require_version ">= 1.7.0"

CONFIG = Hash.new           # GIS.lab configuration
CONFIG_VAGRANT = Hash.new   # GIS.lab configuration for Vagrant (passed as Ansible extra vars)

# GIS.lab configuration
# Read default GIS.lab server machine configuration file
conf = YAML.load_file('system/group_vars/all')
conf.each do |key, value|
  if not value.nil?
    CONFIG[key] = value
  end
end

# Read Configuration file for machine running under Vagrant provisioner.
# Use this file to override default GIS.lab configuration when
# using Vagrant provisioner.
if File.exist?('system/host_vars/gislab_vagrant')
  conf = YAML.load_file('system/host_vars/gislab_vagrant')
  conf.each do |key, value|
    if not value.nil?
      CONFIG[key] = value
    end
  end
end


# Vagrant box
BOX = "%s-canonical" % [CONFIG["GISLAB_UBUNTU_VERSION"]]
### Currently broken, see https://github.com/gislab-npo/gislab/issues/493
BOX_URL = "https://cloud-images.ubuntu.com/%s/current/%s-server-cloudimg-amd64-vagrant.box" % [CONFIG["GISLAB_UBUNTU_VERSION"], CONFIG["GISLAB_UBUNTU_VERSION"]]

# GIS.lab configuration for Vagrant
# super user password
if CONFIG.has_key? 'GISLAB_ADMIN_PASSWORD'
  CONFIG_VAGRANT["GISLAB_ADMIN_PASSWORD"] = CONFIG['GISLAB_ADMIN_PASSWORD']
end

# always force set network device for Vagrant to 'eth1'
CONFIG_VAGRANT["GISLAB_SERVER_NETWORK_DEVICE"] = "eth1"


# Vagrant provisioning
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # fix for https://github.com/ansible/ansible/issues/8644
  ENV['PYTHONIOENCODING'] = "utf-8"

  config.vm.box = BOX
  config.vm.box_url = BOX_URL
  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.ssh.forward_agent = true


  # provisioning
  config.vm.define :gislab_vagrant do |server|
    if CONFIG['GISLAB_SERVER_INTEGRATION'] == true
      if CONFIG['GISLAB_SERVER_MAC']
        server.vm.network "public_network", :mac => CONFIG['GISLAB_SERVER_MAC']
      else
        server.vm.network "public_network"
      end
    else
      server.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'] + ".5"
    end

    # VirtualBox configuration
    server.vm.provider "virtualbox" do |vb, override|
      vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY']]
      vb.customize ["modifyvm", :id, "--cpus", CONFIG['GISLAB_SERVER_CPUS']]
      vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vb.customize ["modifyvm", :id, "--nictype2", "virtio"]

      if CONFIG['GISLAB_SERVER_GUI_CONSOLE'] == true
        vb.gui = true
      end
    end

    # installation
    server.vm.provision "install", type: "ansible" do |ansible|
      ansible.playbook = "system/gislab.yml"

      # verbosity
      if CONFIG['GISLAB_DEBUG_INSTALL'] == true
        ansible.verbose = "vv"
      end

      # ansible variables
      ansible.extra_vars = CONFIG_VAGRANT
    end

    # tests
    if CONFIG['GISLAB_TESTS_ENABLE'] == true
      server.vm.provision "test", type: "ansible" do |ansible|
        ansible.playbook = "system/test.yml"

        # verbosity
        ansible.verbose = "vv"

        # ansible variables
        ansible.extra_vars = CONFIG_VAGRANT
      end
    end

  end
end
