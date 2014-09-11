import os
import hashlib
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from webgis.mapcache import Disk
from webgis.viewer.models import Project_registry
from webgis.viewer.metadata_parser import MetadataParser


class Command(BaseCommand):
	"""Django-admin command for cleaning obsolete map caches of all published projects."""

	help = 'Clean obsolete map caches of all published projects'

	def handle(self, *args, **options):
		cache = Disk(base=os.path.join(settings.MEDIA_ROOT, 'cache'))
		for project_record in list(Project_registry.objects.all()):
			project = project_record.project
			project_hash = hashlib.md5(project).hexdigest()
			project_dir = os.path.join(cache.basedir, project_hash)
			metadata_filename = os.path.join(settings.GISLAB_WEB_PROJECT_ROOT, project+'.meta')
			if os.path.exists(metadata_filename):
				try:
					metadata = MetadataParser(metadata_filename)
					last_publish = int(metadata.publish_date_unix)
				except:
					self.stderr.write("Failed to load '{0}' project's metadata file: '{1}'".format(project, metadata_filename))
				else:
					if os.path.exists(project_dir):
						project_publications = os.listdir(project_dir)
						if project_publications:
							for publish_tag in project_publications:
								if int(publish_tag) != int(last_publish):
									publish_pretty = datetime.datetime.fromtimestamp(int(publish_tag)).strftime("%d.%m.%Y %H:%M:%S")
									self.stdout.write("Cleaning '{0}' project's publication '{1}' ({2})".format(project, publish_tag, publish_pretty))
									try:
										cache.delete_project_cache(project_hash, publish_tag)
									except:
										cache_dir = os.path.join(project_dir, publish_tag)
										self.stderr.write("Failed to delete '{0}' project's publication '{1}' ({2}): {3}".format(project, publish_tag, publish_pretty, cache_dir))
						else:
							# remove empty project's cache folder
							try:
								os.rmdir(project_dir)
							except: pass
			else:
				# project was deleted, clean all existing publications
				self.stdout.write("Cleaning cache of deleted project '{0}'".format(project))
				try:
					cache.delete_project_cache(project_hash)
					project_record.delete()
				except:
					self.stderr.write("Failed to delete '{0}' project's cache: {1}".format(project, project_dir))
