Title: GIS.lab Unit
Order: 15
Slug: gislab-unit

__GIS.lab Unit__ appliance is a hardware solution containing installation of GIS.lab system which is ready for
__immediate plug-and-play deployment__ and user friendly management using __web administration interface__.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab Unit]({filename}/images/gislab-unit.png)  
_GIS.lab Unit appliance_
</div>


# Technical specification
## Hardware
* CPU: Intel Core i5 3427U 1,8 GHz
* RAM: 8 - 16 GB DDR3 Kingston
* Disk: 60 -120 GB SSD Kingston
* Size: 116,6 mm x 39 mm x 112 mm

## Software
### GIS.lab Server
* Deployment: Ansible
* Operating system: Ubuntu Linux
* Authentication: LDAP (OpenLDAP), Kerberos
* DNS: BIND
* Email: Postfix
* Time service: NTP
* Files storage: EXT4, LVM, NFS 4
* Database storage: PostgreSQL/PostGIS
* Monitoring services: Syslog-NG, Logcheck, Munin
* Remote access: VPN (OpenVPN)
* Clustering: HAProxy, Serf
* Communication: IRC (IRCD Hybrid)
* Web services: NGINX, Lighttpd, Django, Gunicorn
* Map services: WMS, WFS (QGIS Server)
* Desktop client boot service: DHCP (ISC DHCP), NBD

### GIS.lab Desktop
* Operating system: Ubuntu Linux
* Desktop environment: XFCE
* Office suite: LibreOffice
* Web browser: Firefox
* Graphics editor: GIMP, Inkscape
* Video player: VLC
* Secure data storage: KeepassX
* Database management: PgAdmin, SpatiaLite GUI
* GIS software: QGIS, GRASS
* Virtual client support: VirtualBox Guest Additions

### GIS.lab Web
* Framework: ExtJS
* Map library: OpenLayers
