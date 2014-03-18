from django.db import models
from datetime import datetime

from product import Product



class Service(Product):
    class Meta:
        db_table = 'services'
        app_label = 'inventory'
