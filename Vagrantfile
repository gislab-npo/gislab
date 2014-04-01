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
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
  config.vm.box = "precise32-canonical"
  
  config.vm.hostname = "server.gis.lab"
  config.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'].strip + ".5"

  config.vm.network :forwarded_port, guest: 111, host: 1111, auto_correct: true
  config.vm.network :forwarded_port, guest: 2049, host: 2049, auto_correct: true

  config.ssh.forward_agent = true

  # VirtualBox provider
  config.vm.provider "virtualbox" do |vb, override|
    override.vm.provision "shell",
      path: "system/install.sh",
      args: "virtualbox"

    vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY'].strip]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
    # vb.gui = true
  end

  # AWS provider
  config.vm.provider :aws do |aws, override|
    # https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box
    override.vm.box = "dummy"

    override.vm.provision "shell",
      path: "system/install.sh",
      args: "aws"

    override.ssh.username = "ubuntu"
    override.ssh.private_key_path = CONFIG['GISLAB_SSH_PRIVATE_KEY'].strip

    aws.access_key_id = CONFIG['GISLAB_SERVER_AWS_ACCESS_KEY_ID'].strip
    aws.secret_access_key = CONFIG['GISLAB_SERVER_AWS_SECRET_ACCESS_KEY'].strip
    aws.keypair_name = CONFIG['GISLAB_SERVER_AWS_KEYPAIR_NAME'].strip

    aws.ami = CONFIG['GISLAB_SERVER_AWS_AMI'].strip
    aws.instance_type = CONFIG['GISLAB_SERVER_AWS_INSTANCE_TYPE'].strip
    aws.region = CONFIG['GISLAB_SERVER_AWS_REGION'].strip
    aws.availability_zone = CONFIG['GISLAB_SERVER_AWS_AVAILABILITY_ZONE'].strip
    aws.security_groups = CONFIG['GISLAB_SERVER_AWS_SECURITY_GROUP'].strip

    # ephemeral storage will be silently ignored in 't1.micro' instances
    aws.block_device_mapping = [
      {
        :DeviceName => "/dev/sdb",
        :VirtualName => "ephemeral0"
      },
      {
        :DeviceName => "/dev/sdc",
        :VirtualName => "ephemeral1"
      }
    ]

    aws.tags = {
        'Name' => 'GIS.lab server'
    }
  end
end
