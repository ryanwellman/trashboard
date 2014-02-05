from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product


class Combo(Product):

    class Meta:
        db_table = 'combos'
        app_label = 'agreement'