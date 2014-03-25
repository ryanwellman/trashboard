from django.db import models
from datetime import datetime
from pricegroup import PriceGroup
from organization import Organization
from pricegroup_membership import PGMembership
from django.db.models import Q, Model
from inventory.models import PriceTable

class Campaign(Model):
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
        return PriceTable.get_prices(pts, asof)



    def get_product_contents(self, asof=None):
        if asof is None:
            asof = datetime.now()

        pts = self.get_pricetables()
        return PriceTable.get_contents(pts, asof)


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.campaign_id, self.name]])

    class Meta:
        ordering = ['campaign_id']
        app_label = 'org'
