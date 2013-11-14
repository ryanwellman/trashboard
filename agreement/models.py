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
	one = models.CharField(max_length=10)
	two = models.CharField(max_length=10)
	three = models.CharField(max_length=10)

	def __unicode__(self):
		return u','.join([	self.name, self.address, self.city, self.state,
							self.zip, self.approved, self.one, self.two, self.three
						])

	def serialize(self):
		return 	{
					"name": self.name,
					"address": self.address,
					"city": self.city,
					"state": self.state,
					"zip": self.zip,
					"approved": self.approved,
					"one": self.one,
					"two": self.two,
					"three": self.three,
				}

	def update_from_dict(self, incoming):
		self.name = incoming.get('name')
		self.address = incoming.get('address')
		self.city = incoming.get('city')
		self.state = incoming.get('state')
		self.zip = incoming.get('zip')
		self.approved = incoming.get('approved')
		self.one = incoming.get('one')
		self.two = incoming.get('two')
		self.three = incoming.get('three')
		self.save()

	class Meta:
		verbose_name = u'Customer Agreement'
		verbose_name_plural = u'Customer Agreements'