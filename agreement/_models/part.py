from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable
from product import Product




class Part(Product):
    class Meta:
        db_table = 'parts'
        app_label = 'agreement'


