from django.db import models
from datetime import datetime

from product import Product
from django.db.models import Q

from collections import defaultdict

class PriceTable(models.Model):
    """
    represents a business entity's unique price table
    each business entity can have a price table which then has others
    layered on top of it later
    """

    pricetable_id  =   models.CharField(max_length=40, primary_key=True)
    products       =   models.ManyToManyField(Product, through='ProductPrice', related_name='ProductPrices')

    @staticmethod
    def get_prices(pricetables, asof):

        pps = []

        # Valid PPs have bounding dates that include asof
        after_from = Q(fromdate__isnull=True) | Q(fromdate__lte=asof)
        before_to = Q(todate__isnull=True) | Q(todate__gt=asof)

        timefilter = after_from & before_to

        # Grab every pp for the pricetables (which are already sorted by zorder)
        # And insert them into a list (so that they will already be sorted by zorder)
        for pt in pricetables:
            pps.extend(list(pt.productprices.filter(timefilter)))

        # Compose two lists of prices
        promo_entries = dict()
        normal_entries = dict()


        # checking just the promo versions
        for pp in pps:
            # For each pp, set it (if it has not already been set) in the appropriate
            # list.
            if pp.promo:
                promo_entries.setdefault(pp.product_id, pp)
            else:
                normal_entries.setdefault(pp.product_id, pp)

        # Make a dictionary of both sets, where promo_entries overwrites normal.
        together_prices = dict(normal_entries, **promo_entries)

        return together_prices

    @staticmethod
    def get_contents(pricetables, asof):

        pcs = []

        # Valid PPs have bounding dates that include asof
        after_from = Q(fromdate__isnull=True) | Q(fromdate__lte=asof)
        before_to = Q(todate__isnull=True) | Q(todate__gt=asof)

        timefilter = after_from & before_to

        # Grab every pp for the pricetables (which are already sorted by zorder)
        # And insert them into a list (so that they will already be sorted by zorder)
        for pt in pricetables:
            pcs.extend(list(pt.productcontents.filter(timefilter)))

        # Compose two lists of prices
        promo_entries = defaultdict(list)
        normal_entries = defaultdict(list)


        # checking just the promo versions
        for pc in pcs:
            # For each pc, set it (if it has not already been set) in the apcropriate
            # list.
            if pc.promo:
                promo_entries[pc.included_in_id].append(pc)
            else:
                normal_entries[pc.included_in_id].append(pc)

        # Make a dictionary of both sets, where promo_entries overwrites normal.
        together_prices = dict(normal_entries, **promo_entries)

        # returns: {'GOLD': [pc, pc, pc]}
        return together_prices



    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.name]])

    class Meta:
        ordering = ['pricetable_id']
        app_label = 'inventory'
