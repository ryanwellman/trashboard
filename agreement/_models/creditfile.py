from django.db import models
from datetime import datetime
from django.utils import timezone
from ..uas import Serializable, Updatable

from creditapplication import CreditApplication


class CreditFile(Serializable):
    """
    represents one credit agency's opinion of how good an applicant's
    ability to repay debt is
    """

    parent = models.ForeignKey(CreditApplication)
    beacon = models.IntegerField(default=0)
    bureau = models.CharField(max_length=20)
    decision = models.CharField(max_length=20)
    date_created = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=64)
    person_id = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=64)
    transaction_status = models.CharField(max_length=20)
    fraud = models.BooleanField(default=False)
    frozen = models.BooleanField(default=False)
    nohit = models.BooleanField(default=False)
    vermont = models.BooleanField(default=False)

    class Meta:
        app_label = 'agreement'
