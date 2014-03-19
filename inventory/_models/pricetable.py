from django.db import models
from datetime import datetime

from product import Product

class PriceTable(models.Model):
    """
    represents a business entity's unique price table
    each business entity can have a price table which then has others
    layered on top of it later
    """

    pricetable_id  =   models.CharField(max_length=40, primary_key=True)
    products       =   models.ManyToManyField(Product, through='ProductPrice', related_name='ProductPrices')

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.name]])

    class Meta:
        ordering = ['pricetable_id']
        app_label = 'inventory'
