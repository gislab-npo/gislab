# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.5.0"

# load GIS.lab configuration file
CONFIG = Hash.new
File.readlines("config.cfg").each do |line|
  values = line.split("=")
  if not values[1].nil?
    CONFIG[values[0]] = values[1].strip.gsub(/["']/, '')
  end
end

if File.exist?('config-user.cfg')
  File.readlines("config-user.cfg").each do |line|
    values = line.split("=")
    if not values[1].nil?
      CONFIG[values[0]] = values[1].strip.gsub(/["']/, '')
    end
  end
end

# override allowed configuration variables from environment
allowed_envs = Array["GISLAB_SERVER_MEMORY", "GISLAB_SERVER_GUI_CONSOLE",
  "GISLAB_SERVER_AWS_ACCESS_KEY_ID", "GISLAB_SERVER_AWS_SECRET_ACCESS_KEY"
]
ENV.each do |envvar|
  if envvar[0].match(/^GISLAB_/) && (allowed_envs.include? envvar[0])
    CONFIG[envvar[0]] = ENV[envvar[0]]
  end
end


# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
  # or
  # http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box
  config.vm.box = "precise-canonical"
  
  config.vm.network "public_network", ip: CONFIG['GISLAB_NETWORK'] + ".5"

  config.ssh.forward_agent = true
  if not CONFIG['GISLAB_SSH_PRIVATE_KEY'].empty?
     config.ssh.private_key_path = [CONFIG['GISLAB_SSH_PRIVATE_KEY'], File.join("system", "insecure_private_key")]
  end

  # VirtualBox provider
  config.vm.provider "virtualbox" do |vb, override|
    override.vm.provision "shell",
      path: "system/install.sh",
      args: "virtualbox"

    vb.customize ["modifyvm", :id, "--memory", CONFIG['GISLAB_SERVER_MEMORY']]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.customize ["modifyvm", :id, "--nictype2", "virtio"]

    if CONFIG['GISLAB_SERVER_GUI_CONSOLE'] == "yes"
      vb.gui = true
    end
  end

  # AWS provider
  config.vm.provider :aws do |aws, override|
    # https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box
    override.vm.box = "dummy"

    override.vm.provision "shell",
      path: "system/install.sh",
      args: "aws"

    config.vm.synced_folder '.', '/vagrant', :rsync_excludes => ['tmp', 'mnt', 'http-boot']

    override.ssh.username = "ubuntu"
    override.ssh.private_key_path = CONFIG['GISLAB_SSH_PRIVATE_KEY']

    aws.access_key_id = CONFIG['GISLAB_SERVER_AWS_ACCESS_KEY_ID']
    aws.secret_access_key = CONFIG['GISLAB_SERVER_AWS_SECRET_ACCESS_KEY']
    aws.keypair_name = CONFIG['GISLAB_SERVER_AWS_KEYPAIR_NAME']

    aws.ami = CONFIG['GISLAB_SERVER_AWS_AMI']
    aws.instance_type = CONFIG['GISLAB_SERVER_AWS_INSTANCE_TYPE']
    aws.region = CONFIG['GISLAB_SERVER_AWS_REGION']
    aws.availability_zone = CONFIG['GISLAB_SERVER_AWS_AVAILABILITY_ZONE']
    aws.security_groups = CONFIG['GISLAB_SERVER_AWS_SECURITY_GROUPS'].strip.gsub(/[()]/, '').split(' ')


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
        'Name' => 'GIS.lab server',
        'GISLAB_UNIQUE_ID' => CONFIG['GISLAB_UNIQUE_ID']
    }
  end
end
