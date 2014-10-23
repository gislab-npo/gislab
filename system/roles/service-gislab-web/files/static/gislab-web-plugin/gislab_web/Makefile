#/***************************************************************************
# GIS.lab Web plugin
# Publish your projects into GIS.lab Web application
# ***************************************************************************/

# CONFIGURATION
QGISDIR=.qgis2

GISLAB_BUILDDIR=build

# Makefile for a PyQGIS plugin

# global
PLUGINNAME = gislab_web

PY_FILES = webgisplugin.py topics.py __init__.py

EXTRAS = icon.png metadata.txt

UI_FILES = publish_dialog.ui

RESOURCE_FILES = resources_rc.py

default: compile

compile: $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<


# The deploy target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(QGISDIR)/python/plugins
deploy: compile
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

# The zip target creates a zip file with the deployed content.
# You can then upload the zip file on http://plugins.qgis.org
zip:
	mkdir -p $(GISLAB_BUILDDIR)/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(GISLAB_BUILDDIR)/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(GISLAB_BUILDDIR)/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(GISLAB_BUILDDIR)/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(GISLAB_BUILDDIR)/$(PLUGINNAME)
	rm -f $(PLUGINNAME).zip
	cd $(GISLAB_BUILDDIR); zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)
	rm -Rf $(GISLAB_BUILDDIR)

clean:
	rm $(RESOURCE_FILES)
