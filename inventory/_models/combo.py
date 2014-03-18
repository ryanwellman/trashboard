from django.db import models
from datetime import datetime
from product import Product


class Combo(Product):

    class Meta:
        db_table = 'combos'
        app_label = 'inventory'