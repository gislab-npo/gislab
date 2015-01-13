Title: GIS.lab server
Submenu: yes
Order: 10
Slug: gislab-server
Status: draft


__GIS.lab server__ is a heart of whole system. It provides basic network services such as central user authentication, client networking configuration, domain names service or email. It also provides __file and geo-database storage__ service and dedicated services for GIS such as __Web Map Service (WMS)__, __Web Feature Service (WFS)__ and __GIS project publishing service GIS.lab Web__.

If deployed in LAN, GIS.lab server also provides network boot service powering __GIS.lab client__ infrastructure which is specially prepared for desktop GIS data processing and analysis.

GIS.lab server can run in automatically provisioned virtual machine (Linux, OS X, MS Windows host system), on bare metal server or in a cloud.


## GIS data storage, management and sharing
Spatial or non-spatial data can be stored, managed and shared in hierarchy of shared directories or in more sophisticated manner in dedicated geo-database storage. This service is accessible also for third party clients which do not run GIS.lab client environment. 

Implemented by: SFTP, SSHFS, NFS 4, PostgreSQL/PostGIS


## OGC Web Services
Raster or vector spatial data managed by GIS.lab server can be shared with any clients using standardized services Web Map Service (WMS) or Web Feature Service (WFS). These services allows delivery of GIS data to any clients using industry standard format.

Implemented by: QGIS Mapserver


## GIS.lab client boot service
One of a core features of GIS.lab server is to provide a network boot service and runtime infrastructure for GIS.lab client systems. Any client machine connected to GIS.lab network can boot in to GIS.lab client environment (physical or virtual) from network. User authentication credentials and data are centrally managed on GIS.lab server and are not tight to particular client machine. Once client machine is started it will always receive clean and up-to-date operating system image and after authentication it will connect to user's data.

Implemented by: ISC DHCP, TFTP, NBD, BIND, OpenLDAP, LTSP


## GIS.lab Web publishing service 
GIS.lab server provides powerful service for instant publishing of GIS projects on web (see more in [GIS.lab Web page](gislab-web))

Implemented by: QGIS Desktop and Mapserver, GIS.lab Web


## Central data backup and recovery
Data backup is implemented in form of user archive packages which contains all data and important settings belonging to particular user and can be easily restored on any GIS.lab system.

Implemented by: GIS.lab management tools
