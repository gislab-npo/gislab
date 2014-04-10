from django.conf import settings
from django.db.models.signals import post_syncdb

from webgis.viewer import models as viewer_models


def _post_syncdb_routines(sender, app, **kwargs):
	if getattr(settings, 'WEBGIS_GUEST_USERNAME', ''):
		user, created = viewer_models.GislabUser.objects.get_or_create(username=settings.WEBGIS_GUEST_USERNAME)
		user.set_unusable_password()
		user.save()

post_syncdb.connect(_post_syncdb_routines, sender=viewer_models, dispatch_uid="viewer.__init__")
