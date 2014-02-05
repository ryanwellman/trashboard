from django.db import models
from datetime import datetime
from django.utils import timezone
from agreement.uas import Serializable, Updatable

from product import Product
from pricetable import PriceTable



class RequiresLine(Serializable):
    """
    represents a requirement by one product of another single product
    indexed on a pricetable

    this is used one way for services and another for incentives
        * if parent is of type 'incentive' the children are things we need
          to activate the incentive

        * if parent is of type anything else, the children are things that
          are mandatory for purchase with the parent
    """

    parent      =   models.ForeignKey(Product, related_name='ParentProduct')
    child       =   models.ForeignKey(Product, related_name='RequiredProduct', blank=True, null=True)
    quantity    =   models.IntegerField(default=1)
    pricetable  =   models.ForeignKey(PriceTable)

    def __unicode__(self):
        fields = []
        try:
            fields.append(self.parent)
            fields.append(self.child)
            fields.append(self.pricetable)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['pricetable']
        app_label = 'agreement'

