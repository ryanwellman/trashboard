from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product
from pricegroup import PriceGroup
from organization import Organization
from pricegroup_membership import PGMembership
from django.db.models import Q

class Campaign(Serializable):
    """
    represents a campaign within an organization.

    most of the time this is synonymous with agent but it
    really means any way the organization wants to
    split up people getting paid
    """

    pricegroup  =   models.ForeignKey(PriceGroup, blank=True, null=True) # this can be blank but an org must have one
    name        =   models.CharField(max_length=80)
    campaign_id =   models.CharField(max_length=32, primary_key=True)
    organization = models.ForeignKey(Organization, related_name='campaigns')

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('pricegroup_id', 'name', 'campaign_id', 'organization_id')
        }
        return jsonable

    def get_pricetables(self):
        """
        get zorders for a given campaign
        """

        # Find the pricegroup for this campaign
        pg = self.pricegroup or self.organization.pricegroup

        # Find all subscribed pricetables (PGMs, ordered by zorder)
        pgms = list(PGMembership.objects.filter(pricegroup=pg).order_by('-zorder'))

        # Get just the pricetables
        pts = [pgm.pricetable for pgm in pgms]

        # Return them.
        return pts

    def get_product_prices(self, asof=None):
        if asof is None:
            asof = datetime.now()

        pts = self.get_pricetables()
        pps = []

        # Valid PPs have bounding dates that include asof
        after_from = Q(fromdate__isnull=True) | Q(fromdate__lte=asof)
        before_to = Q(todate__isnull=True) | Q(todate__gt=asof)

        timefilter = after_from & before_to

        # Grab every pp for the pricetables (which are already sorted by zorder)
        # And insert them into a list (so that they will already be sorted by zorder)
        for pt in pts:
            pps.extend(list(pt.productprice_set.filter(timefilter)))

        # Compose two lists of prices
        promo_prices = dict()
        normal_prices = dict()


        # checking just the promo versions
        for pp in pps:
            # For each pp, set it (if it has not already been set) in the appropriate
            # list.
            if pp.promo:
                promo_prices.setdefault(pp.product_id, pp)
            else:
                normal_prices.setdefault(pp.product_id, pp)

        # Make a dictionary of both sets, where promo_prices overwrites normal.
        together_prices = dict(normal_prices, **promo_prices)

        # Return the product prices as a list.  (Each product appears only once.)
        return together_prices


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.campaign_id, self.name]])

    class Meta:
        ordering = ['campaign_id']
        app_label = 'agreement'
