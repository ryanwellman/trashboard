from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable






class Address(Updatable):
    """
    represents a physical location as blessed by a major postal service
    this field is updatable from a json-like blob
    """

    name = models.CharField(max_length=80)
    street1 = models.CharField(max_length=80)
    street2 = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=2)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('name', 'street1', 'street2', 'city', 'state', 'zip', 'country')
        }
        return jsonable

    def update_from_blob(self, blob, updater=None):
        errors = []
        for field in ('name', 'street1', 'street2', 'city', 'state', 'zip', 'country'):
            setattr(self, field, blob.get(field) or '')

        self.infer_country()

        if updater:
            updater.errors.extend(errors)

    def infer_country(self):
        country = 'US'
        if self.state and self.state in ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']:
            country = 'CA'
        if self.zip and not self.zip.isdigit():
            country = 'CA'
        self.country = country

    def __unicode__(self):
        # street1 city, state, country zip
        # postal codes should go last (?)
        return "{0} {1}, {2}, {4} {3}".format(self.street1, self.city, self.state, self.zip, self.country)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        app_label = 'agreement'