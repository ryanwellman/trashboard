import datetime
from django.core.exceptions import ValidationError
from django.db import models
from agreement.uas import UpdatableAndSerializable

class Product(UpdatableAndSerializable):
    """
    conceptually represents a sort-of upc for anything we sell
    
    products are separated into a set of bins by type
    """

    # ptypes = ['shipping', 'incentives', 'equipment', 'combos', 'ratedrop',
    #          'part', 'service', 'monitoring']

    code        =   models.CharField(max_length=20, primary_key=True)
    type        =   models.CharField(max_length=10)
    category    =   models.CharField(max_length=20)
    name        =   models.CharField(max_length=20)
    description =   models.CharField(max_length=100)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.code, self.name, self.type, self.category]])

    class Meta:
        ordering = ['code']


class PriceTable(UpdatableAndSerializable):
    """
    represents a business entity's unique price table
    each business entity can have a price table which then has others
    layered on top of it later
    """

    group       =   models.CharField(max_length=10, primary_key=True)
    products    =   models.ManyToManyField(Product, through='ProductPrice', related_name='ProductPrices')

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.group]])

    class Meta:
        ordering = ['group']


class ProductPrice(UpdatableAndSerializable):
    """
    represents membership by a product in a price table
    through table for PriceTable and Product

    promo is a tiebreaker thing that flattens the last level of the
    stackable price tables for quick access to one-off promos
    """

    pricetable      =   models.ForeignKey(PriceTable)
    product         =   models.ForeignKey(Product)
    monthly_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    upfront_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    cb_points       =   models.IntegerField(default=0)
    fromdate        =   models.DateTimeField()
    todate          =   models.DateTimeField()
    promo           =   models.BooleanField(default=False)


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.pricetable, self.product, self.monthly_price, self.upfront_price]])

    class Meta:
        ordering = ['pricetable']


class Applicant(UpdatableAndSerializable):
    """
    represents a customer signing an agreement

    might need more fields
    """

    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone = models.CharField(max_length=15)

    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.fname, mid, self.lname)

    class Meta:
        verbose_name = "Applicant"


class Address(UpdatableAndSerializable):
    """
    represents a physical location as blessed by a major postal service
    """

    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=10)

    def __unicode__(self):
        # address city, state, country zip
        # postal codes should go last (?)
        return "{0} {1}, {2}, {4} {3}".format(self.address, self.city, self.state, self.zip, self.country)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


class Package(UpdatableAndSerializable):
    """
    represents a package we sell
    potentially also represents a customized package via PkgProduct's quantity field
    """

    products   =   models.ManyToManyField(Product, through='PkgProduct', related_name='PkgProducts')
    name       =   models.CharField(max_length=50, primary_key=True)
    code       =   models.CharField(max_length=10)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.code, self.name]])

    class Meta:
        ordering = ['name']


class PkgProduct(UpdatableAndSerializable):
    """
    represents membership by a product in a package
    through table for Package and Product
    """

    package    =    models.ForeignKey(Package)
    product    =    models.ForeignKey(Product)
    quantity   =    models.IntegerField(default=0)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.package, self.product, self.quantity]])

    class Meta:
        ordering = ['package']


class Campaign(UpdatableAndSerializable):
    """
    represents a campaign within an organization.

    most of the time this is synonymous with agent but it
    really means any way the organization wants to
    split up people getting paid
    """

    pricetables =   models.ManyToManyField(PriceTable, through='CmpPrice', related_name='Campaigns')
    name        =   models.CharField(max_length=50)
    campaign_id =   models.CharField(max_length=32, primary_key=True)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.campaign_id, self.name]])

    class Meta:
        ordering = ['campaign_id']


class CmpPrice(UpdatableAndSerializable):
    """
    represents membership by a price table in a campaign
    through table for Campaign and PriceTable

    price table overlays occur here for individual campaigns

    see OrgPrice for a detailed explanation
    """

    campaign        =   models.ForeignKey(Campaign)
    pricetable      =   models.ForeignKey(PriceTable)
    date_updated    =   models.DateTimeField()
    notes           =   models.CharField(max_length=30, blank=True)    # still ???
    zorder          =   models.IntegerField(default=0)                 # 'importance'

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.campaign, self.pricetable, self.zorder]])


    class Meta:
        ordering = ['campaign']


class Agreement(UpdatableAndSerializable):
    """
    represents an agreement by a customer to buy our products

    this particular version of Agreement is a shim for the actual Agreement
    which exists in dashboard and may or may not be compatible with this one

    general field reference:
        campaign: who gets paid commission
        applicants: whose credit is going to be run
        addresses: where to bill and where the alarm is
        pricetable_date: what day's prices should be used
        invoice_lines: what did we sell them and how much did we say it cost
        email: how to contact the applicants about this agreement
        approved: what was their credit score like
        package: what box do we use
        shipping: who gets paid to transport the package
        monitoring: who gets paid to watch this system
    
    XXX: fields that depend on things in pricemodels.py are in but commented out
         since we are still adding fields to this as the form takes shape
    XXX: needs a harness to inject test data - making that soon
    """

    campaign = models.ForeignKey(Campaign)
    applicant = models.ForeignKey(Applicant, related_name='main_applicant')
    coapplicant = models.ForeignKey(Applicant, related_name='co_applicant', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing')
    system_address =models.ForeignKey(Address, related_name='system')
    pricetable_date = models.DateField(auto_now_add=True) # automatically timestamped on creation
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=10)
    package = models.ForeignKey(Package, related_name='package')
    shipping = models.CharField(max_length=10)
    monitoring = models.CharField(max_length=10)

    def __unicode__(self):
        if not self.id:
            id_display = u'Unsaved'
        else:
            id_display = unicode(self.id)
        return u','.join([unicode(f) for f in [id_display, self.applicant, self.approved, self.package, self.billing_address, self.system_address]]) # needs campaign_id

    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'


class InvoiceLine(UpdatableAndSerializable):
    """
    crystallizes line items of an Agreement (invoice)

    it is possible for all 6 price fields to be set to None (NULL)!
    """

    import locale
    locale.setlocale(locale.LC_ALL, '')

    agreement       =   models.ForeignKey(Agreement)
    note            =   models.CharField(max_length=50)
    product         =   models.ForeignKey(Product)
    pricetable      =   models.ForeignKey(PriceTable)
    qty             =   models.IntegerField(default=0)
    pricedate       =   models.DateTimeField()
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
        return u','.join([unicode(f) for f in [self.agreement, self.parent, self.note, self.pricedate]])

    class Meta:
        ordering = ['agreement']


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


class ComboLine(UpdatableAndSerializable):
    """
    represents one piece of a combo package
    """

    parent          =   models.ForeignKey(Combo, related_name="ParentCombo") # a product of type combo
    product         =   models.ForeignKey(Product)
    qty             =   models.PositiveIntegerField(default=0)
    upfront_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.parent, self.product]])

    class Meta:
        ordering = ['parent']


class Organization(UpdatableAndSerializable):
    """
    represents an overarching business entity that may
    or may not have multiple 'campaigns' which usually means
    an agent, but is a way of logically separating the
    members of the business for whatever reason

    each organization also has a price table associated with it
    that governs what they charge for our products
    """

    pricetables =   models.ManyToManyField(PriceTable, through='OrgPrice', related_name='Organizations')
    campaigns   =   models.ManyToManyField(Campaign, through='OrgCampaign', related_name='Campaigns')
    name        =   models.CharField(max_length=50)
    provider_id =   models.IntegerField(primary_key=True)

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.name]])

    class Meta:
        ordering = ['name']


class OrgPrice(UpdatableAndSerializable):
    """
    represents membership by a price table in an organization
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

    organization    =   models.ForeignKey(Organization)
    pricetable      =   models.ForeignKey(PriceTable)
    date_updated    =   models.DateTimeField()
    notes           =   models.CharField(max_length=30, blank=True)    # ???
    zorder          =   models.IntegerField(default=0)                 # 'priority'

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.organization, self.pricetable, self.zorder]])

    class Meta:
        ordering = ['organization']


class OrgCampaign(UpdatableAndSerializable):
    """
    represents membership by a campaign in an organization
    through table for Organization and Campaign
    """

    organization    =   models.ForeignKey(Organization)
    campaign        =   models.ForeignKey(Campaign)
    date_updated    =   models.DateTimeField()

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.organization, self.pricetable, self.zorder]])

    class Meta:
        ordering = ['organization']