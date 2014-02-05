from django.db import models
from datetime import datetime
from django.utils import timezone
from ..uas import Serializable, Updatable

from agreement import Agreement




class InvoiceLine(Updatable):
    """
    crystallizes line items of an Agreement (invoice)
    this is what makes custom packages possible

    it is possible for all 6 price fields to be set to None (NULL)!
    this field is updatable from a json-like blob
    """

    import locale
    locale.setlocale(locale.LC_ALL, '')

    agreement       =   models.ForeignKey(Agreement)
    note            =   models.CharField(max_length=50)
    product         =   models.CharField(max_length=20)
    category        =   models.CharField(max_length=64)
    pricetable      =   models.CharField(max_length=20)
    quantity        =   models.IntegerField(default=0)
    pricedate       =   models.DateTimeField(default=timezone.now) # timestamp on save
    upfront_each    =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    upfront_total   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    upfront_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_each    =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_total   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    parent          =   models.ForeignKey('self', blank=True, null=True)
    mandatory       =   models.BooleanField(default=False)

    @property
    def upfront_display(self):
        return self.upfront_strike if self.upfront_strike is not None else self.upfront_total

    @property
    def monthly_display(self):
        return self.monthly_strike if self.monthly_strike is not None else self.monthly_total

    def __unicode__(self):
        fields = [self.note, self.pricedate]
        try:
            fields.append(self.agreement)
            fields.append(self.parent)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['agreement']
        app_label = 'agreement'

