from django.db import models
from datetime import datetime
from django.utils import timezone
from ..uas import Serializable, Updatable
from applicant import Applicant
from address import Address
from campaign import Campaign
from package import Package


class Agreement(Updatable):
    """
    represents an agreement by a customer to buy our products

    this particular version of Agreement is a shim for the actual Agreement
    which exists in dashboard and may or may not be compatible with this one

    general field reference:
        campaign: who gets paid commission
        applicants: whose credit is going to be run
        addresses: where to bill and where the alarm is
        pricetable_date: what day's prices should be used
        email: how to contact the applicants about this agreement
        approved: what was their credit score like
        package: what box do we use
        shipping: who gets paid to transport the package
        monitoring: who gets paid to watch this system
        floorplan: what shape is the target address
        promo_code: just one for now!

    this field is updatable from a json-like blob
    """

    campaign = models.ForeignKey(Campaign)
    applicant = models.ForeignKey(Applicant, related_name='main_applicant')
    coapplicant = models.ForeignKey(Applicant, related_name='co_applicant', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing')
    system_address =models.ForeignKey(Address, related_name='system')
    pricetable_date = models.DateField(default=timezone.now) # automatically timestamped on creation
    date_updated = models.DateField(default=timezone.now) # update when updated
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=20)
    package = models.ForeignKey(Package, related_name='package', blank=True, null=True) # now nullable
    shipping = models.CharField(max_length=20)
    monitoring = models.CharField(max_length=20)
    floorplan = models.CharField(max_length=20)
    promo_code = models.CharField(max_length=20)
    done_premium = models.BooleanField(default=False)
    done_combo = models.BooleanField(default=False)
    done_alacarte = models.BooleanField(default=False)
    done_closing = models.BooleanField(default=False)
    done_package = models.BooleanField(default=False)
    done_promos = models.BooleanField(default=False)

    def __unicode__(self):
        if not self.id:
            id_display = u'Unsaved'
        else:
            id_display = unicode(self.id)

        fields = [id_display, self.approved]
        try:
            fields.append(self.campaign)
            fields.append(self.applicant)
            fields.append(self.package)
            fields.append(self.billing_address)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'
        app_label = 'agreement'
