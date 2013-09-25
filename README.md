Open Source GIS Laboratory
==========================
A purpose of this project is to create easy-to-use, pre-configured, centrally managed and portable GIS laboratory LAN platform based on open source software. All software works out-of-box, without any need of configuration or other behind a scene knowledge, allowing user to keep high focus on his GIS task.

This platform consists from one Linux server instance running LTSP server inside automatically provisioned Virtualbox machine and many diskless client computers running LTSP Fat client. This setup allows to use all client's computer power and it is very friendly to server resources.

Server instance contains:
 * file sharing service (NFS)
 * database server (PostgreSQL/PostGIS)

Every client workstation should contain:
 * complete office desktop suite for internet browsing, email, chat, images and video, word, spreadsheet
 and presentation editing and more
 * set of software equipment for data editing, analysis and database storage and management
 * set of software equipment for GIS development
 * set of high quality free data
 * step by step manuals for the most common tasks


Installation
------------
Sofware requirements:
 * Linux (in our case XUBUNTU 12.04)
 * Virtualbox [1]
 * Vagrant >= 1.3.3 [2]
 * Git

Download a Vagrant box
$ vagrant box add precise32 http://files.vagrantup.com/precise32.box

Download a GIS LAB sources
$ git clone https://github.com/imincik/gis-lab.git

Fire up a Vagrant provisioner
$ cd gis-lab
$ vagrant up

Connect client computers to LAN (PXE), configure them to boot from LAN and enjoy.


IP addresses
------------
LTSP server: 192.168.50.5
LTSP clients: 192.168.50.100-250


Authentication
--------------
By default all user accounts and their password are made as simple as they can.

LTSP server accounts (SSH)
 * vagrant:vagrant

LTSP client accounts
 * lab[1-24]:lab

PostgreSQL
 * labadmin:labadmin
 * lab:lab


LTSP Client in Virtualbox
-------------------------
For development purposes you can configure Virtualbox machine to act as LTSP client.
Important configurations are:
 * you do not need to create any boot hard disk
 * configure boot order to boot only from network (and enable IO APIC)
 * configure network adapter in brigged mode; make sure you select the PCnet-FAST III (Am79C973)
 as the adaptor type; allow promiscuous mode for all
  


WARNING: Currently, this project is in early stage of development. Be patient please.

1 - https://www.virtualbox.org/
2 - http://docs.vagrantup.com/v2/getting-started/index.html
