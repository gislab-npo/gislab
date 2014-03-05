Title: GIS.lab server
Submenu: yes
Order: 10
Slug: gislab-server

# GIS.lab client boot service
One of a core features of GIS.lab server is to provide a network boot service and runtime infrastructure for GIS.lab client systems. Any client machine connected to GIS.lab network can boot client environment (physical or virtual) from network. Users authentication credentials are centrally managed in LDAP database and they are not tight to particular client machine - any client machine can be used by any user as far as his authentication credentials exists in database.

Implemented by: ISC DHCP, TFTP, NBD, BIND, OpenLDAP


# GIS data storage, management and sharing
Spatial or non-spatial data can be stored, managed and shared in hierarchy of shared directories or in more sophisticated manner in dedicated geo-database storage. This service is accessible also for third party clients which do not run GIS.lab client environment. 

Implemented by: SFTP, SSHFS, NFS 4, PostgreSQL/PostGIS


# OGC Web Services
Raster or vector spatial data managed by GIS.lab server can be shared with clients via standardized services such as Web Map Service (WMS) or Web Feature Server (WFS). This interface allows usage of GIS.lab provided data to all clients, including third party clients, via industry standard services.

Implemented by: QGIS Mapserver


# Web GIS publishing service
GIS.lab server provides powerful web GIS project publishing service (see more in [GIS.lab client page](gislab-client))

Implemented by: QGIS Desktop and Mapserver, GIS.lab WebGIS


# Central data backup and recovery
Data backup is implemented in form of user archive packages which contains all important user settings and data and can be easily restored on any GIS.lab system.

Implemented by: GIS.lab management tools
