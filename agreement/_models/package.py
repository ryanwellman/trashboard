from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable
from product import Product


class Package(Product):
    """
    represents a package we sell
    """

    class Meta:
        db_table = 'packages'
        app_label = 'agreement'
