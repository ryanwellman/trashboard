from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable
from product import Product



class Service(Product):
    class Meta:
        db_table = 'services'
        app_label = 'agreement'
