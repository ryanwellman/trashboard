from django.db import models
from cPickle import loads, dumps

class Agreement(models.Model):
	"""
	dummy model, contains a dict
	"""

	fname = models.CharField(max_length=50)
	lname = models.CharField(max_length=50)
	initial = models.CharField(max_length=1)
	address = models.CharField(max_length=80)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=25)
	zip = models.CharField(max_length=10)
	taxid = models.CharField(max_length=15)
	email = models.CharField(max_length=75)
	country = models.CharField(max_length=10)
	approved = models.CharField(max_length=10)
	package = models.CharField(max_length=10)
	shipping = models.CharField(max_length=10)
	monitoring = models.CharField(max_length=10)
	# this stores a serialized array
	completed = models.TextField()


	def __unicode__(self):
		return ','.join(["{0} {1}. {2}".format(self.fname, self.initial, self.lname), self.approved, self.package, self.city, self.state])

	def serialize(self):
		# cpickle loads does not like blank textfields
		# the obvious reason is that dumps([]) does not equal ''
		try:
			complete = loads(str(self.completed))
		except EOFError as e:
			complete = []

		return 	{
					"agreement_id": self.id, # this one is named differently in the javascript
					"fname": self.fname,
					"lname": self.lname,
					"initial": self.initial,
					"address": self.address,
					"city": self.city,
					"state": self.state,
					"zip": self.zip,
					"taxid": self.taxid,
					"email": self.email,
					"country": self.country,
					"approved": self.approved,
					"package": self.package,
					"shipping": self.shipping,
					"monitoring": self.monitoring,
					"completed": complete,
				}

	def update_from_dict(self, incoming):
		self.fname = incoming.get('fname')
		self.lname = incoming.get('lname')
		self.initial = incoming.get('initial')
		self.address = incoming.get('address')
		self.city = incoming.get('city')
		self.state = incoming.get('state')
		self.zip = incoming.get('zip')
		self.taxid = incoming.get('taxid')
		self.email = incoming.get('email')
		self.country = incoming.get('country')
		self.approved = incoming.get('approved')
		self.package = incoming.get('package')
		self.shipping = incoming.get('shipping')
		self.monitoring = incoming.get('monitoring')
		self.completed = dumps(incoming.get('completed'))
		self.save()

	class Meta:
		verbose_name = u'Customer Agreement'
		verbose_name_plural = u'Customer Agreements'