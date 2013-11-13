from django.db import models

class Agreement(models.Model):
	"""
	dummy model, contains a dict
	"""

	name = models.CharField(max_length=50)
	address = models.CharField(max_length=80)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=25)
	zip = models.CharField(max_length=10)
	approved = models.CharField(max_length=10)

	def __unicode__(self):
		return u','.join([self.name, self.address, self.city, self.state, self.zip, self.approved])

	class Meta:
		verbose_name = u'Customer Agreement'
		verbose_name_plural = u'Customer Agreements'