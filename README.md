Open Source GIS Laboratory
==========================
Super easy deployment of fully equipped and unbreakable GIS LAN with one hundred workstations in a few moments.

A purpose of this project is to create  fully equipped, easy-to-use, pre-configured, centrally managed and portable GIS laboratory LAN platform based on open source software. All software works out-of-box, without any need of configuration or other behind a scene knowledge, allowing users to keep high focus on their GIS task.

This platform consists from one Linux server instance running LTSP server inside automatically provisioned Virtualbox machine and many diskless client computers running LTSP Fat client. This setup allows to use all client's computer power and it is very friendly to server resources.

Key features of this platform:
 * super easy fully automatic deployment and maintenance - all operation are encapsulated in easy to use commands
 * nearly zero requirements for client computers - no operating system or software needed, no hard disk needed
 * no limit of number of client computers
 * 100 percent real computer user experience - no thin client glitches
 * central management of all client OS images, user accounts and user data
 * every user can log in from any client computer to get his working environment
 * unbreakable client OS images - after every client reload you always get fresh OS environment
 * rich software equipment of client computers for internet browsing, email, chat, images and video, word, spreadsheet
 and presentation editing and more
 * Linux system security
 * out of box internet sharing from server computer to all client computers
 * out of box working file sharing service (NFS)
 * out of box database server (PostgreSQL/PostGIS)

Key features of GIS implementation on this platform:
 * best tuned set of software equipment for data editing, analysis and database storage and management [PARTIALY IMPLEMENTED]
 * set of software equipment for GIS development [TODO]
 * set of high quality free data [TODO]
 * step by step manuals and how-to documents for the most common tasks [TODO]


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
