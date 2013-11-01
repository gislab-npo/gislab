-- EPSG: 102067 (obsolete) --
-- This definition contains TOWGS parameters common for Czech republic and Slovakia.
-- See: http://grass.fsv.cvut.cz/gwiki/%C4%8Ceskoslovensk%C3%BD_transforma%C4%8Dn%C3%AD_kl%C3%AD%C4%8D

INSERT INTO "spatial_ref_sys" ("srid", "auth_name", "auth_srid", "srtext", "proj4text")
VALUES (102067, 'ESRI', 102067, 'PROJCS["S-JTSK_Krovak_East_North",
GEOGCS["GCS_S_JTSK",DATUM["D_S_JTSK",SPHEROID["Bessel_1841",6377397.155,299.1528128]],
PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Krovak"],
PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Pseudo_Standard_Parallel_1",78.5],
PARAMETER["Scale_Factor",0.9999],PARAMETER["Azimuth",30.28813975277778],
PARAMETER["Longitude_Of_Center",24.83333333333333],PARAMETER["Latitude_Of_Center",49.5],
PARAMETER["X_Scale",-1],PARAMETER["Y_Scale",1],PARAMETER["XY_Plane_Rotation",90],
UNIT["Meter",1]]', '+proj=krovak +lat_0=49.5 +lon_0=24.83333333333333 +alpha=30.28813975277778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel +units=m +no_defs +towgs84=542.5,89.2,456.9,5.517,2.275,5.516,6.96');




-- EPSG: 5514 --
-- This definition contains TOWGS parameters common for Czech republic and Slovakia.
-- See: http://grass.fsv.cvut.cz/gwiki/%C4%8Ceskoslovensk%C3%BD_transforma%C4%8Dn%C3%AD_kl%C3%AD%C4%8D
INSERT INTO "spatial_ref_sys" ("srid", "auth_name", "auth_srid", "srtext", "proj4text")
VALUES (5514, 'ESRI', 5514, 'PROJCS["S-JTSK_Krovak_East_North",
GEOGCS["GCS_S_JTSK",DATUM["D_S_JTSK",SPHEROID["Bessel_1841",6377397.155,299.1528128]],
PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Krovak"],
PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Pseudo_Standard_Parallel_1",78.5],
PARAMETER["Scale_Factor",0.9999],PARAMETER["Azimuth",30.28813975277778],
PARAMETER["Longitude_Of_Center",24.83333333333333],PARAMETER["Latitude_Of_Center",49.5],
PARAMETER["X_Scale",-1],PARAMETER["Y_Scale",1],PARAMETER["XY_Plane_Rotation",90],
UNIT["Meter",1]]', '+proj=krovak +lat_0=49.5 +lon_0=24.83333333333333 +alpha=30.28813975277778 +k=0.9999 +x_0=0 +y_0=0 +ellps=bessel +units=m +no_defs +towgs84=542.5,89.2,456.9,5.517,2.275,5.516,6.96');


-- vim: set ts=2 sts=2 sw=2 noet:
