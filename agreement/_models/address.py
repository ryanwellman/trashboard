from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable






class Address(Updatable):
    """
    represents a physical location as blessed by a major postal service
    this field is updatable from a json-like blob
    """

    name = models.CharField(max_length=80)
    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=10)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('name', 'address', 'city', 'state', 'zip', 'country')
        }
        return jsonable

    def fill_country_from_postal_code(self):
        # source: http://en.wikipedia.org/wiki/List_of_postal_codes
        # canadian postal codes are ANA NAN with an optional space or hyphen between sections
        # usa postal codes are NNNNN with an optional -NNNN added on

        # XXX: regexen for future use maybe?
        # canada: ^[A-CEGHJ-NPRSTVW-Z]\d[A-CEGHJ-NPRSTVW-Z][-\ ]?\d[A-CEGHJ-NPRSTVW-Z]\d$
        # usa: ^\d\d\d\d\d(-\d\d\d\d)?$

        if not self.zip:
            return # can't do anything
        else:
            if self.zip[0].isdigit():
                self.country = 'USA'
            else:
                self.country = 'Canada'

    def __unicode__(self):
        # address city, state, country zip
        # postal codes should go last (?)
        return "{0} {1}, {2}, {4} {3}".format(self.address, self.city, self.state, self.zip, self.country)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        app_label = 'agreement'