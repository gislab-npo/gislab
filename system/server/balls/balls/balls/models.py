import random
import string

from django.db import models


class Ball(models.Model):
	id = models.CharField(u"id", max_length=8, primary_key=True)
	data = models.TextField(u"data")
	mime_type = models.CharField(u"MIME type", max_length=50, blank=True)

	def __unicode__(self):
		return self.id

	def _random_id(self):
		return "".join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for x in range(8))

	def save(self, *args, **kwargs):
		if not self.id:
			random_id = self._random_id()
			while Ball.objects.filter(id=random_id).exists():
				random_id = self._random_id()
			self.id = random_id
		return super(Ball, self).save(*args, **kwargs)
