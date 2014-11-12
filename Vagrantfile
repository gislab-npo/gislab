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
if File.exist?('system/host_vars/gislab_vagrant')
  conf = YAML.load_file('system/host_vars/gislab_vagrant')
  conf.each do |key, value|
    if not value.nil?
      CONFIG[key] = value
    end
  end
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
  # or
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box
  config.vm.box = "precise-canonical"
  
  config.vm.synced_folder '.', '/vagrant', disabled: true

  config.ssh.forward_agent = true
  if not CONFIG['GISLAB_SSH_PRIVATE_KEY'].nil?
    config.ssh.private_key_path = [CONFIG['GISLAB_SSH_PRIVATE_KEY'], File.join("system", "insecure_ssh_key")]
  end


  # GIS.lab server
  config.vm.define :gislab_vagrant do |server|
    server.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'] + ".5"

    # provisioning
    server.vm.provision "ansible" do |ansible|
      ansible.playbook = "system/gislab.yml"
      if CONFIG['GISLAB_DEBUG_INSTALL'] == true
        ansible.verbose = "vv"
      end
      if CONFIG.has_key? 'GISLAB_ADMIN_PASSWORD'
        ansible.extra_vars = { GISLAB_ADMIN_PASSWORD: CONFIG['GISLAB_ADMIN_PASSWORD'] }
      end
    end

    # VirtualBox configuration
    server.vm.provider "virtualbox" do |vb, override|
      vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY']]
      vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vb.customize ["modifyvm", :id, "--nictype2", "virtio"]

      if CONFIG['GISLAB_SERVER_GUI_CONSOLE'] == "yes"
        vb.gui = true
      end
    end
  end


  # GIS.lab worker
  (1..CONFIG['GISLAB_WORKERS_COUNT']).each do |i|
    config.vm.define vm_name = "gislab_vagrant_w%02d" % i do |worker|
      worker.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'] + ".#{9+i}"

    # provisioning
      worker.vm.provision "shell",
        inline: "echo 'Performing worker installation (will take some time) ...' \
          && mkdir -p /tmp/install && cd /tmp/install \
	  && curl --silent http://%s.5/worker.tar.gz | tar xz \
	  && bash ./install.sh &> /var/log/gislab-install-worker.log \
          && echo 'Worker installation is done.'" % [CONFIG['GISLAB_NETWORK']]

      # VirtualBox configuration
      worker.vm.provider "virtualbox" do |vb, override|
        vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_WORKER_MEMORY']]
        vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
      end
    end
  end

end
