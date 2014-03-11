Title: Home
Order: 1
Template: home_page
URL:
save_as: index.html

__GIS.lab provides possibility to automatically deploy GIS server and unlimited number of client machines in a few moments.__

GIS.lab network provides comprehensive set of services and the best collection of Open Source GIS software, seamlessly integrated to one easy to use, centrally managed, portable and unbreakable system. It is designed as standalone, independent system which works out-of-box without any need of configuration. GIS.lab lowers deployment and ownership barrier of complex GIS infrastructure to zero, while still keeping whole technology in house under full control.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab network architecture]({filename}/images/gislab-architecture.png)  
Fig. 1: GIS.lab network architecture
</div>


# Central unit
__GIS.lab server__ is a heart of whole system. It provides service to boot client machines from network and comprehensive set of other services for all connected members. It always runs in automatically provisioned virtual machine which coherently works across all major operating systems (Windows, Linux or Mac OS X). It is up to user's preferences which platform to choose.


# Any computer can be a client
Preferred method of launching __GIS.lab client__ machine is a __physical client mode__. In this mode, client machine is configured to boot a new GIS.lab client environment from GIS.lab server network boot service. Access to original operating system is temporary lost (it can be restored after machine restart without any changes or a danger of loosing data). This mode provides best performance.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab physical client]({filename}/images/schema-physical-client.png)  
Fig. 2: Empty machine or machine running Windows turning to GIS.lab physical client and back
</div>

In case user can't offer loosing access to a system physically installed on client machine, there is a possibility to launch __GIS.lab client__ inside of any Windows, Linux or Mac OS X operating system in __virtual client mode__. This mode will boot the same client environment from GIS.lab server network boot service inside of VirtualBox machine and will allow to run both systems side-by-side. It is possible use GIS.lab virtual client in a windowed mode, similar as it would be a common application or in a fullscreen mode for best user experience.

<div style="text-align:center;padding:10px" markdown="1">
![GIS.lab virtual client]({filename}/images/schema-virtual-client.png)  
Fig. 3: Machine running Windows launching GIS.lab virtual client
</div>

In a both modes, client machine runs fully featured operating system capable to use client's hardware potential when minimizing server load on the other side.


# Third party clients
Any third-party computers can be connected to GIS.lab network without requirement to launch GIS.lab client environment (in physical or virtual mode) and use some set of network services like Internet sharing, file sharing, geo-database and OWS services or access to GIS projects via GIS.lab WebGIS web application. 


# Utilization
* Virtual desktop infrastructure deployment for GIS based businesses
* Education and Open Source GIS software advocacy
* Rapid deployment of crisis management command center network with GIS support
* Parallel computing


# Other benefits
* Open Source software
* No hard dependency on any other Internet service (with exception on OSM and Google maps)
* General usage platform (not limited to GIS)
* Extremely low maintenance costs
    * zero time to install new client machine
    * central distribution of client systems with rollback
    * rapid recovery from hardware failure
* High performance client systems (opposite of thin client)
