# QGIS2.conf

```
[PythonPlugins]
{% if GISLAB_GISQUICK_INTEGRATION %}
gisquick=true
{% endif %}

[Qgis]
customEnvVarsUse=true
customEnvVars="overwrite|TMPDIR=/mnt/booster", "overwrite|GRASS_VECTOR_TEMPORARY=move", "overwrite|GRASS_VECTOR_TMPDIR_MAPSET=0"

[PostgreSQL]
connections\selected=gislab@server.gis.lab
connections\gislab%40server.gis.lab\host=server.gis.lab
connections\gislab%40server.gis.lab\port=5432
connections\gislab%40server.gis.lab\database=gislab
connections\gislab%40server.gis.lab\username={+ GISLAB_USER +}
connections\gislab%40server.gis.lab\saveUsername=true
connections\gislab%40server.gis.lab\savePassword=true

[browser]
expandedPaths=favourites:
favourites=/mnt/home/{+ GISLAB_USER +}/.grassdata, /mnt/home/{+ GISLAB_USER +}/Projects, /mnt/home/{+ GISLAB_USER +}/Publish, /mnt/home/{+ GISLAB_USER +}/Repository

[GRASS]
gidbase\custom=true
gidbase\customDir=/usr/lib/grass72
lastGisdbase=/mnt/home/{+ GISLAB_USER +}/.grassdata
windows\tools\geometry=@ByteArray(\x1\xd9\xd0\xcb\0\x1\0\0\0\0\b\x9d\0\0\0\x91\0\0\n\xee\0\0\x3\x18\0\0\b\x9d\0\0\0\x91\0\0\n\xee\0\0\x3\x18\0\0\0\0\0\0)
```