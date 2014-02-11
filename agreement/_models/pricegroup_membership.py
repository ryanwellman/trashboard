from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product
from pricegroup import PriceGroup
from pricetable import PriceTable




class PGMembership(Serializable):
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
        app_label = 'agreement'
