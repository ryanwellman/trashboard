from django.db import models
from datetime import datetime

from inventory.models import Product, PriceTable

from django.db.models import Model



class PriceGroup(Model):
    """
    represents a group of providers or campaigns that all use the same stack of price tables
    """

    pricetables     =   models.ManyToManyField(PriceTable, through='PGMembership', related_name='pricetables')
    name            =   models.CharField(max_length=64)

    def __unicode__(self):
        fields = [self.name]
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['name']
        app_label = 'org'
