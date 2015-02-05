import random
import string

from django.db import models


class Ball(models.Model):
	id = models.CharField(u"id", max_length=109, primary_key=True)
	user = models.CharField(u"user", max_length=100, blank=False)
	data = models.TextField(u"data")
	sender = models.CharField(u"sender", max_length=100, blank=False)
	mime_type = models.CharField(u"MIME type", max_length=50, blank=False)
	timestamp = models.DateTimeField("time stamp", auto_now_add=True)

	class Meta:
		ordering = ["timestamp"]

	def __unicode__(self):
		return self.id

	def _random_id(self):
		return "".join(random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for x in range(8))

	def save(self, *args, **kwargs):
		if not self.id:
			random_id = self._random_id()
			while Ball.objects.filter(id=random_id).exists():
				random_id = self._random_id()
			self.id = "{0}:{1}".format(self.user, random_id)
		return super(Ball, self).save(*args, **kwargs)


class Drawing(models.Model):
	user = models.CharField(u"user", max_length=100, blank=False)
	project = models.TextField(u"project")
	title = models.CharField(u"title", max_length=255, blank=False)
	timestamp = models.DateTimeField(u"time stamp", auto_now_add=True)
	ball = models.ForeignKey(Ball, verbose_name=u"ball")
	permalink = models.TextField(u"permalink")
	statistics = models.TextField(u"statistics")

	def __unicode__(self):
		return self.title

	class Meta:
		index_together = [
			["user", "project"],
		]
		ordering = ["-timestamp"]
