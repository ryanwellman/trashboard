from django.db import models
from datetime import datetime
from pricetable import PriceTable
from product import Product


class PricetableEntry(models.Model):
    pricetable      =   models.ForeignKey(PriceTable, related_name='%(class)ss')
    fromdate        =   models.DateTimeField(null=True)
    todate          =   models.DateTimeField(null=True)
    promo           =   models.BooleanField(default=False)

    class Meta:
        abstract = True

class ProductPrice(PricetableEntry):
    """
    represents membership by a product in a price table
    through table for PriceTable and Product

    promo is a tiebreaker thing that flattens the last level of the
    stackable price tables for quick access to one-off promos
    """

    product         =   models.ForeignKey(Product)
    max_quantity    =   models.IntegerField(blank=True, null=True)
    monthly_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    upfront_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    cb_points       =   models.IntegerField(default=0, blank=True, null=True)
    swappable       =   models.BooleanField(default=False)
    # Should be listed in a cart
    available       =   models.BooleanField(default=True)


    @property
    def entry_code(self):
        return self.product_id

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.pricetable, self.product, self.monthly_price, self.upfront_price]])

    def as_jsonable(self):
        d = dict(
            code=self.product_id,
            max_quantity=self.max_quantity,
            monthly_price=self.monthly_price,
            upfront_price=self.upfront_price,
            cb_points=self.cb_points,
            fromdate=self.fromdate,
            todate=self.todate,
            promo=self.promo,
            swappable=self.swappable,
            available=self.available,
        )
        if getattr(self, 'available_mask', None) is not None:
            d['available'] = self.available_mask

        return d

    class Meta:
        ordering = ['pricetable']
        app_label = 'inventory'
