Open Source GIS Laboratory
==========================
A purpose of this project is to create easy-to-use, pre-configured, centrally managed and portable GIS laboratory LAN platform based on open source software. All software should work out-of-box without any need of configuration or other behind a scene knowledge, allowing user to keep high focus on his GIS task.

This platform consists from one Linux computer running LTSP server inside automatically provisioned Virtualbox machine and many diskless client computers running LTSP Fat client. This setup allows to use all client's computer power and it is very friendly to server resources.

Every workstation should contain:
 * set of software equipment for data editing, analysis and database storage and management
 * set of software equipment for development
 * set of high quality free data
 * step by step manuals for the most common tasks


Installation
------------
Sofware requirements:
 * Linux (in our case XUBUNTU 12.04)
 * Virtualbox [1]
 * Vagrant [2]
 * Git

Download a Vagrant box
$ vagrant box add precise32 http://files.vagrantup.com/precise32.box

Download a GIS LAB sources
$ git clone https://github.com/imincik/gis-lab.git

Fire up a Vagrant provisioner
$ cd gis-lab
$ vagrant up

Connect client computers to LAN (PXE), configure them to boot from LAN and enjoy.


WARNING: Currently, this project is in early stage of development. Be patient please.

1 - https://www.virtualbox.org/
2 - http://docs.vagrantup.com/v2/getting-started/index.html
