from django.db import models
from datetime import datetime


from django.db.models import Model
from pricegroup import PriceGroup

class Organization(Model):
    """
    represents an overarching business entity that may
    or may not have multiple 'campaigns' which usually means
    an agent, but is a way of logically separating the
    members of the business for whatever reason

    each organization also has a price group associated with it
    that governs what they charge for our products
    """

    pricegroup =    models.ForeignKey(PriceGroup) # must have this
    #campaigns   =   models.ManyToManyField(Campaign, through='OrgCampaign', related_name='Campaigns')
    name        =   models.CharField(max_length=50)
    provider_id =   models.CharField(max_length=32, primary_key=True)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.name, self.provider_id]])

    class Meta:
        ordering = ['name']
        app_label = 'org'

'''
class OrgCampaign(Serializable):
    """
    represents membership by a campaign in an organization
    through table for Organization and Campaign

    because these things have price groups they need a zorder too
    """

    organization    =   models.ForeignKey(Organization)
    campaign        =   models.ForeignKey(Campaign)
    date_updated    =   models.DateTimeField()
    zorder          =   models.IntegerField(default=0)

    def __unicode__(self):
        fields = [self.date_updated]
        try:
            fields.append(self.organization)
            fields.append(self.campaign)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['organization']
'''

