from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product


class Closer(Product):

    class Meta:
        db_table = 'closers'
        app_label = 'agreement'

