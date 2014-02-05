from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable
from product import Product




class Shipping(Product):
    class Meta:
        db_table = 'shipping_methods'
        app_label = 'agreement'