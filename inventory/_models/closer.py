from django.db import models
from datetime import datetime
from product import Product


class Closer(Product):

    class Meta:
        db_table = 'closers'
        app_label = 'inventory'

