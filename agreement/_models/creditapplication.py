from django.db import models
from datetime import datetime
from django.utils import timezone
from agreement.uas import Serializable, Updatable

from applicant import Applicant


class CreditApplication(Serializable):
    """
    represents a set of credit files for one of our applicants
    """

    applicant = models.ForeignKey(Applicant)
    decision = models.CharField(max_length=20)
    override_by = models.CharField(max_length=64, blank=True, null=True)
    override_date = models.DateField(default=timezone.now, blank=True, null=True)
    reference_id = models.IntegerField(default=0)

    class Meta:
        app_label = 'agreement'
