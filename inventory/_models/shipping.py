from django.db import models
from datetime import datetime

from product import Product




class Shipping(Product):
    class Meta:
        db_table = 'shipping_methods'
        app_label = 'inventory'