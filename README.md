GIS.lab - Open Source GIS office
================================
Super easy deployment of fully equipped GIS office with unlimited number of workstations in a few moments.

GIS.lab provides possibility to create fully equipped, easy-to-use, pre-configured, centrally managed, portable and unbreakable GIS office platform from one host machine running central server and unlimited number of diskless client machines. All software works out-of-box, without any need of configuration or other behind a scene knowledge, allowing users to keep high focus on their GIS task.

The platform consists from one Linux server instance running LTSP server inside automatically provisioned Virtualbox machine and unlimited diskless client machines running LTSP Fat client. This setup allows to use all client machine power and it is very friendly to server resources.

Key features:
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
 * out of box working backup service [TODO]
 * Linux system security
 * great platform for studying open source technologies beginning from Linux OS, various system services and end user software
 * best tuned set of software equipment for data editing, analysis and database storage and management [PARTIALY IMPLEMENTED]
 * set of software equipment for scripting and GIS software development [TODO]
 * out of box working web GIS publishing solution
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

Download latest GIS.lab package from https://github.com/imincik/gis-lab/releases

or

clone GIS.lab sources if You are developer or familiar with Git
```
$ git clone https://github.com/imincik/gis-lab.git
```

Allow client MAC addresses in config.cfg:
 * add your MACs to GISLAB_CLIENTS_ALLOWED (recommended)
 * or set GISLAB_UNKNOWN_MAC_POLICY=allow

Fire up a Vagrant provisioner
```
$ cd gis-lab
$ vagrant up
```

Connect host machine to client machines via gigabit switch and cable (CAT 5e or higher)

Configure client machines BIOS to boot from LAN (PXE) or use boot manager (usually activated by F12 early on start) and enjoy

Do not forget to shut down GIS.lab server before shutting down host machine
```
$ vagrant halt
```


Upgrade
-------
Currently, in this phase of development we provide only hard upgrade process where whole system including data
is going to be replaced. Later we will add much more sophisticated approach. Please backup your data !

Update GIS.lab sources
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

Server accounts (SSH)
 * vagrant:vagrant

PostgreSQL
 * lab[1-12]:lab

Default client accounts
 * lab[1-12]:lab


LTSP Client in Virtualbox
-------------------------
For development purposes you can configure Virtualbox machine to act as LTSP client.
Important configurations are:
 * you do not need to create any boot hard disk
 * configure boot order to boot only from network (and enable IO APIC)
 * configure network adapter in bridged mode; make sure you select the PCnet-FAST III (Am79C973)
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


Working with GIS.lab
--------------------
### User accounts
By default, user accounts specified in GISLAB_USER_ACCOUNTS_AUTO are created automatically after installation.
You can also create or delete additional accounts manually:
 * '$ vagrant ssh -c "sudo gislab-adduser.sh <username>"' - create account
 * '$ vagrant ssh -c "sudo gislab-deluser.sh <username>"' - delete account


### File sharing
GIS.lab offers out-of-box file sharing solution inside its LAN. All client users can find three different shared
directories in their home directory, each one with different access policy:
 * Repository: directory with read-only permissions for users
 * Share: directory with read permissions for anybody and write permissions for file owner
 * Barrel: directory with read and write permissions for all files for all users

It is possible to mount 'Barrel' shared directory from host machine using 'utils/mount-barrel.sh' script. It is
always good idea to umount it before shutting down GIS.lab server. If forgotten try to umount it with '-fl' options.


### Built-in automatic WMS Viewer viewer
One of the nice features of GIS.lab is WMS Viewer application which is automatically generated for
each user's QGIS project.
Simply save a QGIS project and all file data to '~/Share/<USERNAME>' directory with setting these required configuration:
 * use relative paths (File > Project Properties > General > Save paths). The safest way is to save Your data and project
   file to same directory
 * on-the-fly CRS transformation must be enabled (File > Project Properties > CRS) and target projection
   must be chosen (if You are not sure chose EPSG:3857)
 * OWS advertised extent must be enabled (File > Project Properties > OWS server)
 * for better performance limit number of supported CRSs ((File > Project Properties > OWS server > CRS restrictions)

and launch following URL in a web browser:
```
format:
http://webgis.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>

* PATH-TO-QGIS-PROJECT-FILE must be relative to '~/Share' directory

example of user 'lab1' who saved 'Central Europe' project file packaged with GIS.lab to ~/Share directory ($ cp -a ~/Repository/data/natural-earth ~/Share/$USER):
http://webgis.gis.lab/?PROJECT=lab1/natural-earth/central-europe.qgs

```

Additionally, it is possible to configure behavior of WebGIS app via GET parameters in URL.
```
format:
http://webgis.gis.lab/?PROJECT=<PATH-TO-QGIS-PROJECT-FILE>&<PARAMETER>=<value>&<PARAMETER>=<value>...

```

Supported GET parameters:
 * DPI: DPI resolution of map layers. Example: 120. Default: 96. 
 * SCALES: available list of scales of map. Example: 10000,5000,2500. Default: 1000000,500000,250000,100000,50000,25000,10000,5000,2500,1000,500
 * ZOOM: zoom level to use on start. Example: 2. Default: 0
 * CENTER: coordinates of map center on start. Example: 1234.12,5678.56. Default is center of auto-detected extent from project.
 * OSM: determines if OpenStreetMap base layer will be added to map. Works only in projection EPSG:3857. Example: true. Default is false.
 * LAYERS: list of layers to display in map. Example: border,lakes,rivers. Default is auto-detected list of layers from project.
 * VISIBLE: list of layers to set as visible on application start. Example: border. Default: all layers
 * POINTS: list of vector points to draw on map. Format: <coordinate1>,<coordinate2>,<label>|<coordinate1>,<coordinate2>,<label>|... Example: 1234,5678,nice place|2345,6789,another nice place

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
