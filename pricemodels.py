from django.db import models
from django.core.exceptions import ValidationError

"""
new price models draft
"""

class Product(models.Model):
    """
    conceptually represents a sort-of upc for anything we sell
    
    products are separated into a set of bins by type
    """

    # ptypes = ['shipping', 'incentives', 'equipment', 'combos', 'ratedrop',
    #          'part', 'service', 'monitoring', 'package']

    code        =   CharField(max_length=20, primary_key=True)
    type        =   CharField(max_length=10)
    category    =   CharField(max_length=20)

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([code, type, category]) + ">"

    class Meta:
        ordering = ['code']


class PriceTable(models.Model):
    """
    represents a business entity's unique price table
    each business entity can have a price table which then has others
    layered on top of it later
    """

    group = CharField(max_length=10, primary_key=True)

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([group]) + ">"

    class Meta:
        ordering = ['group']


class Agreement(models.Model):
    """
    ??? - works like an invoice but has other things in it
    """

    def __unicode__(self):
        pass

    class Meta:
        pass


class InvoiceLine(models.Model):
    """
    crystallizes line items of an Agreement (invoice)

    it is possible for all 6 price fields to be set to None (NULL)!
    """

    import locale
    locale.setlocale(locale.LC_ALL, '')

    agreement       =   ForeignKey(Agreement)
    note            =   CharField(max_length=50)
    product         =   ForeignKey(Product)
    pricetable      =   ForeignKey(PriceTable)
    qty             =   IntegerField(default=0)
    pricedate       =   DateTimeField()
    upfront_each    =   DecimalField(blank=True, null=True)
    upfront_total   =   DecimalField(blank=True, null=True)
    upfront_strike  =   DecimalField(blank=True, null=True)    
    monthly_each    =   DecimalField(blank=True, null=True)
    monthly_total   =   DecimalField(blank=True, null=True)
    monthly_strike  =   DecimalField(blank=True, null=True)
    parent          =   ForeignKey('self', blank=True, null=True)
    mandatory       =   BooleanField(default=False)

    @property
    def upfront_display(self):
        return self.upfront_strike if self.upfront_strike is not None else self.upfront_total

    @property
    def monthly_display(self):
        return self.monthly_strike if self.monthly_strike is not None else self.monthly_total

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([agreement, parent, note, pricedate]) + ">"

    class Meta:
        ordering = ['agreement']


class ComboLine(models.Model):
    """
    represents one piece of a combo package
    """

    parent          =   ForeignKey(Product) # a product of type combo
    product         =   ForeignKey(Product)
    qty             =   PositiveIntegerField(default=0)
    upfront_strike  =   DecimalField(blank=True, null=True)
    monthly_strike  =   DecimalField(blank=True, null=True)

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([parent, product]) + ">"

    class Meta:
        ordering = ['parent']


class Combo(Product):
    """
    represents a combo package as a product
    """

    pass


class Incentive(Product):
    """
    represents an incentive as a product
    """

    pass


class RateDrop(Product):
    """
    represents a rate drop as a product
    """

    pass


class OrgPrice(models.Model):
    """
    through table for Organization and PriceTable

    price table overlays occur here for individual organizations
    by comparing the z-order of their associated OrgPrices

    this is done by unioning the results in descending
    z-order and taking the top result

    by default price tables overlay in the reverse order
    they were added; newer prices are used before older ones.
    in the case that this is not the right thing,
    these recipes may help:
        * you want to insert a global base table?
            + use a small negative number in the AutoField
        * you want to insert a specific override?
            + use a big positive number in the AutoField
        * anything else?
            + you will have to recalculate z-order unless there's
              space between price table z-orders.
    """

    organization    =   ForeignKey(Organization)
    pricetable      =   ForeignKey(PriceTable)
    date_updated    =   DateTimeField()
    notes           =   CharField(max_length=30, blank=True)    # ???
    zorder          =   IntegerField(default=0)                 # 'priority'

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([organization, pricetable, zorder]) + ">"

    class Meta:
        ordering = ['organization']


class Organization(models.Model):
    """
    represents an overarching business entity that may
    or may not have multiple 'campaigns' which usually means
    an agent, but is a way of logically separating the
    members of the business for whatever reason

    each organization also has a price table associated with it
    that governs what they charge for our products
    """

    pricetables =   ManyToManyField(PriceTable, through='OrgPrice', related_name='Organizations')
    name        =   CharField(max_length=50)
    provider_id =   IntegerField(primary_key=True)

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([name]) + ">"

    class Meta:
        ordering = ['name']


class CmpPrice(models.Model):
    """
    through table for Campaign and PriceTable

    price table overlays occur here for individual campaigns

    see OrgPrice for a detailed explanation
    """

    campaign        =   ForeignKey(Campaign)
    pricetable      =   ForeignKey(PriceTable)
    date_updated    =   DateTimeField()
    notes           =   CharField(max_length=30, blank=True)    # still ???
    zorder          =   IntegerField(default=0)                 # 'importance'

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([campaign, pricetable, zorder]) + ">"


    class Meta:
        ordering = ['campaign']


class Campaign(models.Model):
    """
    represents a campaign within an organization.

    most of the time this is synonymous with agent but it
    really means any way the organization wants to
    split up people getting paid
    """

    pricetables =   ManyToManyField(PriceTable, through='CmpPrice', related_name='Campaigns')
    name        =   CharField(max_length=50)
    campaign_id =   CharField(max_length=32, primary_key=True)

    def __unicode__(self):
        return "<" + self.__class__.__name__ + ":" + ','.join([name]) + ">"

    class Meta:
        ordering = ['name']