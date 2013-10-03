Open Source GIS Laboratory
==========================
Super easy deployment of fully equipped and unbreakable GIS LAN with unlimited number of workstations in a few moments.

A purpose of this project is to create fully equipped, easy-to-use, pre-configured, centrally managed and portable GIS laboratory LAN platform from one host machine running central server and unlimited number of diskless client machines. All software is configured to work out-of-box, without any need of configuration or other behind a scene knowledge, allowing users to keep high focus on their GIS task.

The platform consists from one Linux server instance running LTSP server inside automatically provisioned Virtualbox machine and unlimited diskless client machines running LTSP Fat client. This setup allows to use all client machine power and it is very friendly to server resources.

Key features of this platform:
 * super easy fully automatic deployment and maintenance - all operation are encapsulated in easy to use commands
 * nearly zero requirements for client machines - no operating system or software needed, no hard disk needed
 * no limit of number of client machines
 * 100 percent real computer user experience - no thin client glitches
 * central management of all client OS images, user accounts and user data
 * every user can log in from any client machine to get his working environment
 * unbreakable client OS images - after every client reload you always get fresh OS environment
 * rich software equipment of client machines for internet browsing, email, chat, images and video, word, spreadsheet
 and presentation editing and more
 * out of box internet sharing from host machine to all client machines
 * out of box working file sharing service (NFS)
 * out of box database server (PostgreSQL/PostGIS)
 * Linux system security
 * great platform for studying open source technologies beginning from Linux OS, various system services and end user software

Key features of GIS implementation on this platform:
 * best tuned set of software equipment for data editing, analysis and database storage and management [PARTIALY IMPLEMENTED]
 * set of software equipment for GIS development [TODO]
 * set of high quality free data [TODO]
 * step by step manuals and how-to documents for the most common tasks [TODO]


Installation
------------
BIG FAT WARNING: Server installed to virtual machine contains its own DHCP server. DHCP server access is restricted 
by MAC addresses when GISLAB_UNKNOWN_MAC_POLICY=deny. Do not change this configuration when you are connecting to Your corporate LAN
and allways consult it with Your sysadmin.
You are absolutely safe to install with GISLAB_UNKNOWN_MAC_POLICY=allow on machine without ethernet connection to any existing LAN.

Installation will NOT modify anything on Your host machine (everything is done inside of virtual machine), no need to worry in this case.

Sofware requirements:
 * Linux (in our case XUBUNTU 12.04)
 * Virtualbox
 * Vagrant >= 1.3.3
 * Git

Download a Vagrant box
```
$ vagrant box add precise32 http://files.vagrantup.com/precise32.box
```

Download latest GIS LAB package from https://github.com/imincik/gis-lab/releases

or

clone GIS LAB sources if You are developer or familiar with Git
```
$ git clone https://github.com/imincik/gis-lab.git
```

Adjust configuration in config.cfg (not required, all default values works)

Add client machines MAC addresses in allowed-clients.cfg (only required if GISLAB_UNKNOWN_MAC_POLICY=deny)

Fire up a Vagrant provisioner
```
$ cd gis-lab
$ vagrant up
```

Connect host machine to client machines via gigabit switch and cable (CAT 5e or higher)

Configure client machines BIOS to boot from LAN (PXE) or use boot manager (usually activated by F12 early on start) and enjoy

Do not forget to shut down GIS LAB server before shutting down host machine
```
$ vagrant halt
```


Upgrade
-------
Currently, in this phase of development we provide only hard upgrade process where whole system including data
is going to be replaced. Later we will add much more sophisticated approach. Please backup your data !

Update GIS LAB sources
```
$ git pull
```

Shutdown all client machines and destroy server
```
$ vagrant destroy
```

Install new version
```
$ vagrant up
```


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
  

Tips
----
Add secondary IP address to host machine to enable connection from host machine to client machines
```
$ ip addr add 192.168.50.2/24 dev eth0
```
remove it with
```
$ ip addr del 192.168.50.2/24 dev eth0
```


Authors
-------
 * Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


Most important technologies and credits
---------------------------------------
 * VirtualBox - https://www.virtualbox.org/
 * XUBUNTU Linux - http://xubuntu.org/
 * Vagrant - http://docs.vagrantup.com/
 * LTSP - http://www.ltsp.org/
 * GDAL - http://www.gdal.org/
 * GEOS - http://geos.osgeo.org/
 * PostgreSQL - http://www.postgresql.org/
 * PgAdmin - http://www.pgadmin.org/
 * PostGIS - http://postgis.net/
 * SpatiaLite - http://www.gaia-gis.it/gaia-sins/
 * QGIS - http://www.qgis.org/
 * GRASS GIS - http://grass.osgeo.org/
 * and many more nice open source projects
