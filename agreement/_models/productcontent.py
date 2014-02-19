from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product




class ProductContent(Serializable):
    """
    represents membership by a product in a package
    through table for Package and Product
    """

    included_in         =    models.ForeignKey(Product, related_name='contents')
    included_product    =    models.ForeignKey(Product, related_name='+')
    quantity            =    models.IntegerField(default=0)
    min_quantity        =    models.IntegerField(default=0) # Only used for package contents.

    upfront_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)
    monthly_strike  =   models.DecimalField(decimal_places=4, max_digits=20, blank=True, null=True)

    @property
    def code(self):
        return self.included_product_id

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
            min_quantity=self.min_quantity,
            upfront_strike=self.upfront_strike,
            monthly_strike=self.monthly_strike,
        )
        return jsonable

    class Meta:
        db_table = 'product_content'
        app_label = 'agreement'

