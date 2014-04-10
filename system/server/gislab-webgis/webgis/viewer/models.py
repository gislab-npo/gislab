from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class GislabUser(AbstractUser):
	organization = ""

	@classmethod
	def get_guest_user(cls):
		if getattr(settings, 'WEBGIS_GUEST_USERNAME', None):
			if not hasattr(cls, 'guest_user'):
				guest_user = None
				try:
					guest_user = GislabUser.objects.get(username=settings.WEBGIS_GUEST_USERNAME)
					guest_user.backend = "django.contrib.auth.backends.ModelBackend"
				except GislabUser.DoesNotExist:
					pass
				cls.guest_user = guest_user
			return cls.guest_user

	@property
	def is_guest(self):
		return self.username == getattr(settings, 'WEBGIS_GUEST_USERNAME', '')

	def get_profile(self):
		return None

	def get_full_name(self):
		full_name = super(GislabUser, self).get_full_name()
		return full_name or self.username

	def __unicode__(self):
		return self.username
