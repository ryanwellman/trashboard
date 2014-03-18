from django.db import models
from datetime import datetime
from django.db.models import Model


from pricegroup import PriceGroup
from inventory.models import PriceTable




class PGMembership(Model):
    """
    through table for PriceGroup and PriceTable so the things can stack
    """

    pricegroup      =   models.ForeignKey(PriceGroup)
    pricetable      =   models.ForeignKey(PriceTable)
    date_updated    =   models.DateTimeField()
    notes           =   models.CharField(max_length=200, blank=True)
    zorder          =   models.IntegerField(default=0)

    def __unicode__(self):
        fields = [self.zorder, self.date_updated]
        try:
            fields.append(self.pricegroup)
            fields.append(self.pricetable)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['pricegroup']
        app_label = 'org'
