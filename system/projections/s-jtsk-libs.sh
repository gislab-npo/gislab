#!/bin/sh

### EPSG: 102067 (obsolete) ###
# These definitions contains TOWGS parameters common for Czech republic and Slovakia.
# See: http://grass.fsv.cvut.cz/gwiki/%C4%8Ceskoslovensk%C3%BD_transforma%C4%8Dn%C3%AD_kl%C3%AD%C4%8D

# proj4
sed -i "s/^<102067>.*/<102067> +proj=krovak +lat_0=49.5 +lon_0=24.83333333333333 +alpha=30.28813975277778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel +units=m +no_defs +towgs84=542.5,89.2,456.9,5.517,2.275,5.516,6.96 <>/"  /usr/share/proj/esri /usr/share/proj/esri.extra

# GDAL
sed -i "s/^102067.*/102067,PROJCS["S-JTSK_Krovak_East_North",GEOGCS["GCS_S_JTSK",DATUM["Jednotne_Trigonometricke_Site_Katastralni",SPHEROID["Bessel_1841",6377397.155,299.1528128],TOWGS84[511.9,92.0,437.3,6.305,2.823,5.944,12.2]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Krovak"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Pseudo_Standard_Parallel_1",78.5],PARAMETER["Scale_Factor",0.9999],PARAMETER["Azimuth",30.28813975277778],PARAMETER["Longitude_Of_Center",24.83333333333333],PARAMETER["Latitude_Of_Center",49.5],PARAMETER["X_Scale",-1],PARAMETER["Y_Scale",1],PARAMETER["XY_Plane_Rotation",90],UNIT["Meter",1],AUTHORITY["EPSG","102067"]]/"  /usr/share/gdal/1.10/esri_extra.wkt




### EPSG: 5514 ###
# These definitions contains TOWGS parameters common for Czech republic and Slovakia.
# See: http://grass.fsv.cvut.cz/gwiki/%C4%8Ceskoslovensk%C3%BD_transforma%C4%8Dn%C3%AD_kl%C3%AD%C4%8D

# proj4
cat << EOF >> /usr/share/proj/epsg
<5514> +proj=krovak +lat_0=49.5 +lon_0=24.83333333333333 +alpha=30.28813975277778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel +units=m +no_defs +towgs84=542.5,89.2,456.9,5.517,2.275,5.516,6.96 <>
EOF


# vim: set ts=4 sts=4 sw=4 noet:
