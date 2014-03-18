from django.db import models
from datetime import datetime


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




class Product(models.Model):
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
        #for pc in self.contents.all():
        #    contents.append(pc.as_jsonable())

        return jsonable

    @staticmethod
    def get_all_products():

        products = []

        # Get all Package objects with type 'package', all Part objects with type 'part',
        # etc etc.  (Already concreted)
        for product_type, product_kls in __typemap__.iteritems():
            products.extend(list(product_kls.objects.filter(product_type=product_type)))

        # Index all the products.
        products = {p.code: p for p in products}

        return products


    def __unicode__(self):
        return u','.join([unicode(f) for f in [self.code, self.name, self.product_type, self.category]])

    class Meta:
        ordering = ['code']
        app_label = 'inventory'