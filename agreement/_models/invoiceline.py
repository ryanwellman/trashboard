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
    # Line type is one of: TOP, TRADE, MANDATORY, CHILD, PERMIT
    line_type       =   models.CharField(max_length=16)
    tag             =   models.CharField(max_length=50)
    product         =   models.CharField(max_length=20)
    #product_name    =   models.CharField(max_length=128)
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
    note            =   models.CharField(max_length=128)

    '''
    This function got too complex.
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
    '''

    def reset(self):
        self.monthly_each = self.monthly_total = None
        self.upfront_each = self.upfront_total = None
        self.upfront_strike = self.monthly_strike = None
        self.cb_points = None

    def update_product(self, product, quantity):
        self.quantity = quantity
        self.product = product.code
        self.product_type = product.product_type
        self.category = product.category

    def update_top(self, product, quantity, price, pricedate):
        # Update this line, which is a top line, using a product that has a price and a pricedate.
        self.line_type = 'TOP'
        self.update_product(product, quantity)

        # erase anything in upfront/monthly/cb that doesn't make sense anymore.
        self.reset()

        self.pricedate = pricedate
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

    def update_mandatory(self, product, quantity, price, pricedate):
        self.update_top(product=product, quantity=quantity, price=price, pricedate=pricedate)

        self.line_type='MANDATORY'

    def update_trade(self, product, quantity, price, pricedate):
        self.line_type = 'TRADE'
        self.update_product(product, quantity)

        # erase anything in upfront/monthly/cb that doesn't make sense anymore.
        self.reset()

        # Trade lines have these because this is what decides its cb_points value.
        self.pricedate = pricedate
        self.pricetable = price.pricetable_id

        self.cb_points = price.cb_points * quantity

    def update_child(self, product, pc, parent_line):
        self.line_type = 'CHILD'
        self.update_product(product, pc.quantity * parent_line.quantity)

        self.reset()
        self.upfront_strike = pc.upfront_strike
        self.monthly_strike = pc.monthly_strike

        self.pricetable = parent_line.pricetable
        self.pricedate = parent_line.pricedate

    def update_permit(self, pr, permit_product):
        self.line_type = 'PERMIT'
        self.update_product(permit_product, 1)

        self.reset()

        # pr is a RequirementsData from restrictions.py (for now)
        pnote = pnote = ';'.join([pr.override_type or pr.region_type, ', '.join(pr.override_name or pr.region_name)])
        self.note=pnote

        self.upfront_each = self.upfront_total = pr.permit_fee
        self.monthly_each = self.monthly_total = pr.addendum_fee
        self.quantity = 1


    @property
    def code(self):
        return self.product

    @property
    def traded(self):
        return self.line_type == 'TRADE'

    @property
    def mandatory(self):
        return self.line_type == 'MANDATORY'

    @property
    def top(self):
        return self.line_type == 'TOP'


    @property
    def upfront_display(self):
        return self.upfront_strike if self.upfront_strike is not None else self.upfront_total

    @property
    def monthly_display(self):
        return self.monthly_strike if self.monthly_strike is not None else self.monthly_total

    def __unicode__(self):

        return 'InvoiceLine(%r)' % self.as_jsonable()

    def as_jsonable(self):
        jsonable = dict()
        for field in ('id', 'note', 'product', 'category',
                      'pricetable', 'pricedate',
                      'quantity',
                      'upfront_each', 'upfront_total', 'upfront_strike',
                      'monthly_each', 'monthly_total', 'monthly_strike',
                      'line_type', 'code'):
            jsonable[field] = getattr(self, field)
        jsonable['parent_id'] = self.parent_id

        return jsonable

    class Meta:
        ordering = ['agreement']
        app_label = 'agreement'

