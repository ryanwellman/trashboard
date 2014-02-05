from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable
from product import Product





class PriceGroup(Serializable):
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
        app_label = 'agreement'
