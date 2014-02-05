from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable






class Address(Updatable):
    """
    represents a physical location as blessed by a major postal service
    this field is updatable from a json-like blob
    """

    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=10)

    def __unicode__(self):
        # address city, state, country zip
        # postal codes should go last (?)
        return "{0} {1}, {2}, {4} {3}".format(self.address, self.city, self.state, self.zip, self.country)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        app_label = 'agreement'