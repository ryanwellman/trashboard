from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from agreement.uas import Updatable, Serializable
from django.db.models import Q


__typemap__ = dict()
class ProductRegistry(models.base.ModelBase):
    def __init__(cls, name, bases, dct):
        # When a workorder model is created
        # Let modelbase do its django-magic
        super(ProductRegistry, cls).__init__(name, bases, dct)

        # Grab the type_code off the class and store it in __typemap__
        type_code = getattr(cls, 'type_code', cls.__name__)
        __typemap__[type_code] = cls
        __typemap__[type_code.lower()] = cls

    @staticmethod
    def get_product_type(code):
        return __typemap__.get(code)




class Product(Serializable):
    __metaclass__ = ProductRegistry

    """
    conceptually represents a sort-of upc for anything we sell

    products are separated into a set of bins by type

    XXX: pricefunctions and the view use category to discriminate between products
    """

    # ptypes = ['shipping', 'incentives', 'equipment', 'combo', 'closer',
    #          'part', 'service', 'monitoring']

    code        =   models.CharField(max_length=64, primary_key=True)
    product_type =   models.CharField(max_length=64)
    category    =   models.CharField(max_length=64)
    name        =   models.CharField(max_length=64)
    description =   models.CharField(max_length=255)

    contentproducts = models.ManyToManyField("self", through='ProductContent', related_name='included_in', symmetrical=False)


    def concrete(self):
        # Get type_code off of self's class (however this instance was currently loaded)
        type_code = getattr(self.__class__, 'type_code', self.__class__.__name__)
        if type_code != self.product_type:
            return __typemap__[self.product_type].objects.get(pk=self.pk)

        return self

    def as_jsonable(self):
        contents = [];
        jsonable = dict(
            code=self.code,
            product_type=self.product_type,
            category=self.category,
            name=self.name,
            description=self.description,
            contents=contents,
        )
        for pc in self.contents.all():
            contents.append(pc.as_jsonable())

        return jsonable


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.code, self.name, self.product_type, self.category]])

    class Meta:
        ordering = ['code']
        app_label = 'agreement'



class PriceTable(Serializable):
    """
    represents a business entity's unique price table
    each business entity can have a price table which then has others
    layered on top of it later
    """

    name        =   models.CharField(max_length=40, primary_key=True)
    products    =   models.ManyToManyField(Product, through='ProductPrice', related_name='ProductPrices')

    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.name]])

    class Meta:
        ordering = ['name']
        app_label = 'agreement'


class ProductPrice(Serializable):
    """
    represents membership by a product in a price table
    through table for PriceTable and Product

    promo is a tiebreaker thing that flattens the last level of the
    stackable price tables for quick access to one-off promos
    """

    pricetable      =   models.ForeignKey(PriceTable)
    product         =   models.ForeignKey(Product)
    max_quantity    =   models.IntegerField(blank=True, null=True)
    monthly_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    upfront_price   =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    cb_points       =   models.IntegerField(default=0)
    fromdate        =   models.DateTimeField(null=True)
    todate          =   models.DateTimeField(null=True)
    promo           =   models.BooleanField(default=False)
    swappable       =   models.BooleanField(default=False)


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.pricetable, self.product, self.monthly_price, self.upfront_price]])

    def as_jsonable(self):
        d = dict(
            code=self.product_id,
            max_quantity=self.max_quantity,
            monthly_price=self.monthly_price,
            upfront_price=self.upfront_price,
            cb_points=self.cb_points,
            fromdate=self.fromdate,
            todate=self.todate,
            promo=self.promo,
            swappable=self.swappable,

        )

    class Meta:
        ordering = ['pricetable']
        app_label = 'agreement'


class Applicant(Updatable):
    """
    represents a customer signing an agreement

    might need more fields
    this field is updatable from a json-like blob
    """

    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone = models.CharField(max_length=15)
    last4 = models.CharField(max_length=4)

    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.fname, mid, self.lname)

    class Meta:
        verbose_name = "Applicant"
        app_label = 'agreement'


class Address(Updatable):
    """
    represents a physical location as blessed by a major postal service
    this field is updatable from a json-like blob
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
        app_label = 'agreement'


class Package(Product):
    """
    represents a package we sell
    """

    class Meta:
        db_table = 'packages'
        app_label = 'agreement'

class Monitoring(Product):
    """
    represents a package we sell
    """

    class Meta:
        db_table = 'monitorings'
        app_label = 'agreement'

class Combo(Product):

    class Meta:
        db_table = 'combos'
        app_label = 'agreement'

class Closer(Product):

    class Meta:
        db_table = 'closers'
        app_label = 'agreement'


class Service(Product):
    class Meta:
        db_table = 'services'
        app_label = 'agreement'

class Shipping(Product):
    class Meta:
        db_table = 'shipping_methods'
        app_label = 'agreement'

class Part(Product):
    class Meta:
        db_table = 'parts'
        app_label = 'agreement'



class ProductContent(Serializable):
    """
    represents membership by a product in a package
    through table for Package and Product
    """

    included_in         =    models.ForeignKey(Product, related_name='contents')
    included_product    =    models.ForeignKey(Product, related_name='+')
    quantity            =    models.IntegerField(default=0)

    upfront_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)


    def __unicode__(self):
        fields = []
        try:
            fields.append(self.package)
            fields.append(self.product)
        except ObjectDoesNotExist:
            pass

        return u','.join([unicode(f) for f in fields])

    def as_jsonable(self):
        jsonable = dict(
            code=self.included_product_id,
            quantity=self.quantity,
            upfront_strike=self.upfront_strike,
            monthly_strike=self.monthly_strike,
        )
        return jsonable

    class Meta:
        db_table = 'product_content'
        app_label = 'agreement'




class PriceGroup(Serializable):
    """
    represents a group of providers or campaigns that all use the same stack of price tables
    """

    pricetables     =   models.ManyToManyField(PriceTable, through='PGMembership', related_name='pricetables')
    name            =   models.CharField(max_length=64)

    def __unicode__(self):
        fields = [self.name]
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['name']
        app_label = 'agreement'


class PGMembership(Serializable):
    """
    through table for PriceGroup and PriceTable so the things can stack
    """

    pricegroup      =   models.ForeignKey(PriceGroup)
    pricetable      =   models.ForeignKey(PriceTable)
    date_updated    =   models.DateField()
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


class Organization(Serializable):
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
        app_label = 'agreement'

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



class Campaign(Serializable):
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
        pps = []

        # Valid PPs have bounding dates that include asof
        after_from = Q(fromdate__isnull=True) | Q(fromdate__lte=asof)
        before_to = Q(todate__isnull=True) | Q(todate__gt=asof)

        timefilter = after_from & before_to

        # Grab every pp for the pricetables (which are already sorted by zorder)
        # And insert them into a list (so that they will already be sorted by zorder)
        for pt in pts:
            pps.extend(list(pt.productprice_set.filter(timefilter)))

        # Compose two lists of prices
        promo_prices = dict()
        normal_prices = dict()


        # checking just the promo versions
        for pp in pps:
            # For each pp, set it (if it has not already been set) in the appropriate
            # list.
            if pp.promo:
                promo_prices.setdefault(pp.product_id, pp)
            else:
                normal_prices.setdefault(pp.product_id, pp)

        # Make a dictionary of both sets, where promo_prices overwrites normal.
        together_prices = dict(normal_prices, **promo_prices)

        # Return the product prices as a list.  (Each product appears only once.)
        return together_prices.values()


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.campaign_id, self.name]])

    class Meta:
        ordering = ['campaign_id']
        app_label = 'agreement'


class Agreement(Updatable):
    """
    represents an agreement by a customer to buy our products

    this particular version of Agreement is a shim for the actual Agreement
    which exists in dashboard and may or may not be compatible with this one

    general field reference:
        campaign: who gets paid commission
        applicants: whose credit is going to be run
        addresses: where to bill and where the alarm is
        pricetable_date: what day's prices should be used
        email: how to contact the applicants about this agreement
        approved: what was their credit score like
        package: what box do we use
        shipping: who gets paid to transport the package
        monitoring: who gets paid to watch this system
        floorplan: what shape is the target address
        promo_code: just one for now!

    this field is updatable from a json-like blob
    """

    campaign = models.ForeignKey(Campaign)
    applicant = models.ForeignKey(Applicant, related_name='main_applicant')
    coapplicant = models.ForeignKey(Applicant, related_name='co_applicant', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing')
    system_address =models.ForeignKey(Address, related_name='system')
    pricetable_date = models.DateField(default=timezone.now) # automatically timestamped on creation
    date_updated = models.DateField(default=timezone.now) # update when updated
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=20)
    package = models.ForeignKey(Package, related_name='package', blank=True, null=True) # now nullable
    shipping = models.CharField(max_length=20)
    monitoring = models.CharField(max_length=20)
    floorplan = models.CharField(max_length=20)
    promo_code = models.CharField(max_length=20)
    done_premium = models.BooleanField(default=False)
    done_combo = models.BooleanField(default=False)
    done_alacarte = models.BooleanField(default=False)
    done_closing = models.BooleanField(default=False)
    done_package = models.BooleanField(default=False)
    done_promos = models.BooleanField(default=False)

    def __unicode__(self):
        if not self.id:
            id_display = u'Unsaved'
        else:
            id_display = unicode(self.id)

        fields = [id_display, self.approved]
        try:
            fields.append(self.campaign)
            fields.append(self.applicant)
            fields.append(self.package)
            fields.append(self.billing_address)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'
        app_label = 'agreement'


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


'''
class ComboLine(Serializable):
    """
    represents one piece of a combo package
    """

    parent          =   models.ForeignKey(Product, related_name="ParentCombo") # a product of type combo
    product         =   models.ForeignKey(Product)
    quantity        =   models.PositiveIntegerField(default=0)
    upfront_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)

    def __unicode__(self):
        fields = [self.quantity, self.upfront_strike, self.monthly_strike]
        try:
            fields.append(self.parent)
            fields.append(self.product)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        ordering = ['parent']
'''


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



class Credit(Serializable):
    """
    represents a set of credit files for one of our applicants
    """

    applicant = models.ForeignKey(Applicant)
    decision = models.CharField(max_length=20)
    override_by = models.CharField(max_length=64, blank=True, null=True)
    override_date = models.DateField(default=timezone.now, blank=True, null=True)
    reference_id = models.IntegerField(default=0)

    class Meta:
        app_label = 'agreement'


class CreditFile(Serializable):
    """
    represents one credit agency's opinion of how good an applicant's
    ability to repay debt is
    """

    parent = models.ForeignKey(Credit)
    beacon = models.IntegerField(default=0)
    bureau = models.CharField(max_length=20)
    decision = models.CharField(max_length=20)
    date_created = models.DateField(default=timezone.now)
    name = models.CharField(max_length=64)
    person_id = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=64)
    transaction_status = models.CharField(max_length=20)
    fraud = models.BooleanField(default=False)
    frozen = models.BooleanField(default=False)
    nohit = models.BooleanField(default=False)
    vermont = models.BooleanField(default=False)

    class Meta:
        app_label = 'agreement'
