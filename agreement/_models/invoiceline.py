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

    agreement       =   models.ForeignKey(Agreement, related_name='invoice_lines')
    note            =   models.CharField(max_length=128)
    tag             =   models.CharField(max_length=50)
    product         =   models.CharField(max_length=20)
    product_type    =   models.CharField(max_length=20)
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
    cb_points       =   models.IntegerField(blank=True, null=True)
    parent          =   models.ForeignKey('self', blank=True, null=True)
    mandatory       =   models.BooleanField(default=False)
    traded          =   models.BooleanField(default=False)

    def update(self, quantity, product, price, pricedate, traded=False):
        self.quantity = quantity
        self.product = product.code
        self.product_type = product.product_type
        self.category = product.category
        self.note = ''
        self.traded = traded

        if pricedate:
            self.pricedate = pricedate

        if traded:

            self.cb_points = price.cb_points * quantity
            self.monthly_each = self.monthly_total = self.upfront_each = self.upfront_total = None
        elif price:
            self.pricetable = price.pricetable_id

            self.upfront_each = price.upfront_price
            if self.upfront_each is None:
                self.upfront_total = None
            else:
                self.upfront_total = self.quantity * self.upfront_each

            self.monthly_each = price.monthly_price
            if self.monthly_each is None:
                self.monthly_total = None
            else:
                self.monthly_total = self.quantity * self.monthly_each

    @property
    def code(self):
        return self.product

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

    def as_jsonable(self):
        jsonable = dict()
        for field in ('id', 'note', 'product', 'category',
                      'pricetable', 'pricedate',
                      'quantity',
                      'upfront_each', 'upfront_total', 'upfront_strike',
                      'monthly_each', 'monthly_total', 'monthly_strike',
                      'mandatory', 'traded', 'code'):
            jsonable[field] = getattr(self, field)
        jsonable['parent_id'] = self.parent_id

        return jsonable

    class Meta:
        ordering = ['agreement']
        app_label = 'agreement'

