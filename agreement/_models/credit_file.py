from django.db import models
from datetime import datetime
from applicant import Applicant
from django.conf import settings

class CreditRequest(models.Model):
    '''
    Represents a REQUEST to run credit one or more times for an applicant.
    Belongs to an applicant so that we know which applicant and agreement,
    specifically, we actually ran credit for.
    '''
    applicant = models.ForeignKey(Applicant)

    # person_id is used to identify the name/social used to run it.
    person_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    last_4 = models.IntegerField()

    # The social is stored in social_data, encrypted with the social_data_key
    # and encoded as base64.  The full social is destroyed as soon as it
    # is no longer needed.
    social_data = models.TextField(null=True, blank=True, default=None)
    social_data_key = models.TextField(null=True, blank=True)
    # comma separated list of bureaus on which to run the request.
    bureaus = models.CharField(max_length=64)
    # Stop running bureaus if you get a response that is at least this value.
    stop_running_at_beacon = models.IntegerField(null=True, blank=True)

    # When and where this was run.
    insert_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    processor_pid = models.IntegerField(blank=True, null=True)

    processed = models.BooleanField(default=False)
    # need to store these things
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    country_code = models.CharField(max_length=10)

    @staticmethod
    def create_request(applicant, social):
        req = CreditRequest()
        req.applicant = applicant
        req.first_name = applicant.first_name
        req.last_name = applicant.last_name
        req.country_code = 'CA'
        req.name = ' '.join(filter(None, [applicant.first_name, applicant.last_name]))
        req.person_id = Applicant.generate_person_id(applicant.first_name, applicant.last_name, social)
        req.social_data, req.social_data_key = settings.SOCIAL_CIPHER.encrypt_long_encoded(social)
        req.bureaus = settings.CREDIT_BUREAUS
        req.last_4 = str(social)[-4:]
        req.stop_running_at_beacon = settings.STOP_RUNNING_AT_BEACON
        req.save()

        return req

    class Meta:
        verbose_name = "Credit Request"
        app_label = 'agreement'


class CreditFile(models.Model):
    '''
    Represents the results of a CreditRequest.  These belong to an applicant,
    but may be duplicated onto another applicant if one exists within the
    correct timeframe, skipping the CreditRequest step.
    '''
    # A given applicant should always have its own credit files.
    # It may have one per bureau?  We need to look at this.

    # Credit files are not reused or shared among applicants.  They'll be
    # copied instead, by using the person_id ( below)
    applicant = models.ForeignKey(Applicant, related_name='credit_file')

    # person_id is used to identify the name/social used to run it.
    person_id = models.CharField(max_length=128)
    name = models.CharField(max_length=64)
    last_4 = models.IntegerField()

    # Then, a new file can be created by COPYING this one if the person_id
    # matches.
    copy_of_file = models.ForeignKey('self', null=True, blank=True, related_name='files')
    # The CreditRequest that generated this credit file, or null if it was a copy.
    # (We can always find it from copy_of_file, and storing a null prevents
    # duplicates from showing in the run's .files list.)
    run_request = models.ForeignKey('CreditRequest', null=True, blank=True)

    # The time that this file was generated.
    generated_date = models.DateTimeField()

    # The result information.
    bureau = models.CharField(max_length=20)
    beacon = models.IntegerField(null=True, blank=True)
    fraud = models.BooleanField(default=False)
    frozen = models.BooleanField(default=False)
    nohit = models.BooleanField(default=False)
    vermont = models.BooleanField(default=False)

    # bookkeeping
    transaction_id = models.CharField(max_length=64)
    transaction_status = models.CharField(max_length=20)


    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.fname, mid, self.lname)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('name', 'bureau', 'fraud', 'frozen', 'nohit', 'vermont', 'beacon', 'generated_date', 'status_string')
        }
        return jsonable

    @property
    def status_string(self):
        if self.fraud or self.frozen or self.vermont:
            return 'REVIEW'
        if self.nohit:
            return 'NO HIT'
        if self.beacon >= settings.CREDIT_APPROVED_BEACON:
            return 'APPROVED'
        return 'DCS'


    class Meta:
        verbose_name = "Credit File"
        app_label = 'agreement'


