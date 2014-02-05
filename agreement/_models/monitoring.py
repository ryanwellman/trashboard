from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable
from product import Product


class Monitoring(Product):
    """
    represents a package we sell
    """

    class Meta:
        db_table = 'monitorings'
        app_label = 'agreement'
