from django.db import models
from datetime import datetime
from django.utils import timezone
from ..uas import Serializable, Updatable
from applicant import Applicant
from address import Address
from campaign import Campaign
from package import Package
from product import Product
from handy import intor, first
from collections import defaultdict
from handy.controller import JsonResponse
import regional.restrictions as restrictions

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
    applicant = models.ForeignKey(Applicant, null=True, blank=True, related_name='+')
    coapplicant = models.ForeignKey(Applicant, null=True, blank=True, related_name='+')
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='billing')
    system_address =models.ForeignKey(Address, null=True, blank=True, related_name='system')
    pricetable_date = models.DateTimeField(default=timezone.now) # automatically timestamped on creation
    date_updated = models.DateTimeField(default=timezone.now) # update when updated
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=20)
    package = models.ForeignKey(Package, related_name='package', blank=True, null=True) # now nullable
    shipping = models.CharField(max_length=20)
    monitoring = models.CharField(max_length=20)

    install_method = models.CharField(max_length=20, blank=True, null=True)
    property_type = models.CharField(max_length=20, blank=True, null=True)
    floorplan = models.CharField(max_length=20, blank=True, null=True)
    promo_code = models.CharField(max_length=20)

    credit_status = models.CharField(max_length=20, null=True, blank=True)
    credit_override = models.CharField(max_length=20, null=True, blank=True)
    #credit_override_user = models.ForeignKey(OrgUser, null=True, blank=True)
    bypass_upfront_authorization = models.BooleanField(default=False)

    # DRAFT, PUBLISHED, EXPIRED, SIGNED
    status = models.CharField(max_length=20)

    @property
    def masked_credit_status(self):
        return self.credit_override or self.credit_status

    def calculate_credit_status(self, socials=None):
        # Return the overall credit status for this agreement.
        # If socials are provided and credit files don't exist for th
        # applicants already, they'll be passed in to the applicants'
        # get_credit_status function so that they can begin running it.
        socials = socials or {}

        applicant = self.applicant
        coapplicant = self.coapplicant
        applicant_status = coapplicant_status = None
        applicant_beacon = None
        if applicant:
            applicant_status = applicant.get_credit_status(social=socials.get('applicant'))
            applicant_beacon = applicant.get_beacon()

        should_start_coapplicant = bool(applicant_status and applicant_status != 'APPROVED')
        if coapplicant:
            # The coapplicant is GOING to get run, because we just got their
            # social and this is the only time to run it (unless we save it somewhere,
            # which I'm loathe to do outside of the request itself, which can get purged.)
            coapplicant_status = coapplicant.get_credit_status(social=socials.get('coapplicant'))

            # # Only run the coapplicant's credit if the applicant isn't approved or pending.
            # should_start = bool(applicant_status and applicant_status not in ('APPROVED', 'PENDING')

            # # Also run the coapplicant's credit if the applicant was approved but under the ideal level.
            # if applicant_status == 'APPROVED' and applicant_beacon < 625:
            #     should_start = True
            # # only run the coapplicant's
            # coapplicant_status = coapplicant.get_credit_status(start_running=should_start_coapplicant)

        # Statuses are: None (not run), PENDING, APPROVED, DCS, NO HIT, REVIEW
        # If either is approved, the agreement's status is approved.
        both = (applicant_status, coapplicant_status)
        if 'APPROVED' in both:
            return 'APPROVED'

        if 'PENDING' in both:
            return 'PENDING'

        if 'REVIEW' in both:
            return 'REVIEW'

        if 'NO HIT' in both:
            return 'NO HIT'

        if 'DCS' in both:
            return 'DCS'

        # If none of these five are in either, the only thing left i
        # (None, None) which means nothing has been run.
        assert(both == (None, None))
        return None

    def available_install_methods(self):
        zipcode = self.system_address.zip if self.system_address else None
        if not zipcode:
            zipcode = None

        return restrictions.get_available_install_methods(
            zipcode=zipcode,
            property_type=self.property_type,
            restriction_date=self.pricetable_date
        )


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

    def as_jsonable(self):
        jsonable = dict()
        for field in ('campaign', 'applicant', 'coapplicant',
                      'billing_address', 'system_address',
                      ):
            obj = getattr(self, field)
            jsonable[field] = obj.as_jsonable() if obj else None

        # primitives
        for field in ('pricetable_date', 'date_updated', 'email',
                      'approved', 'promo_code', 'floorplan',
                    'property_type', 'install_method',
                    'status'):
            jsonable[field] = getattr(self, field)

        jsonable['credit_status'] = self.masked_credit_status
        jsonable['invoice_lines'] = [il.as_jsonable() for il in self.invoice_lines.all()]


        return jsonable


    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'
        app_label = 'agreement'

