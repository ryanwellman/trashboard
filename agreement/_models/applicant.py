from django.db import models
from datetime import datetime
from agreement.uas import Serializable, Updatable





class Applicant(Updatable):
    """
    represents a customer signing an agreement

    might need more fields
    this field is updatable from a json-like blob
    """

    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone = models.CharField(max_length=15)
    last4 = models.CharField(max_length=4)

    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.fname, mid, self.lname)

    class Meta:
        verbose_name = "Applicant"
        app_label = 'agreement'

