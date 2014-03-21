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
    last_4 = models.CharField(max_length=4)

    # The social is stored in social_data, encrypted with the social_data_key
    # and encoded as base64.  The full social is destroyed as soon as it
    # is no longer needed.
    social_data = models.TextField(null=True, blank=True, default=None)
    social_data_key = models.TextField(null=True, blank=True)
    # comma separated list of bureaus on which to run the request.
    bureaus = models.CharField(max_length=64)
    # Stop running bureaus if you get a response that is at least this value.
    stop_running_at_beacon = models.IntegerField(null=True, blank=True)
    approved_at_beacon = models.IntegerField()

    # When and where this was run.
    insert_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    processor_pid = models.IntegerField(blank=True, null=True)

    processed = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    # need to store these things
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=10)
    country_code = models.CharField(max_length=10)

    @staticmethod
    def create_request(applicant, social, social_type):
        req = CreditRequest()
        req.applicant = applicant
        active_agreement = applicant.agreement

<<<<<<< HEAD
        system_address = active_agreement.system_address
=======
        # pre-processors for the country information
        def process_country(info):
            if not info:
                return None
            elif info.upper() in ['CANADA', 'CA']:
                return 'CA'
            else:
                return  'US'

        def process_state(info):
            if not info:
                return None
            elif info.upper() in ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']:
                return 'CA'
            else:
                return  'US'

        def process_zip(info):
            if not info:
                return None
            elif not info[0].isdigit():
                return 'CA'
            else:
                return  'US'

        # figure out which one of these things contains something useful
        # XXX: put these in order of preference
        country_info =  [   process_country(active_agreement.system_address.country),
                            process_state(active_agreement.system_address.state),
                            process_zip(active_agreement.system_address.zip),
                        ]
        try:
            # let's try to get the first useful value
            active_country_info = next((info for info in country_info if info is not None))
        except StopIteration:
            # because brian said so
            return None
>>>>>>> 6d09c91465d6fab398823b65389a593e2e43b713

        # we need this person's SYSTEM address to run their credit
        req.address = ' '.join([active_agreement.system_address.street1, active_agreement.system_address.street2])
        req.city = active_agreement.system_address.city
        req.state = active_agreement.system_address.state
        req.zipcode = active_agreement.system_address.zip
        req.country_code = active_country_info

        # obtain their name
        req.first_name = applicant.first_name
        req.last_name = applicant.last_name
<<<<<<< HEAD

        req.country_code = social_type
        req.name = ' '.join(filter(None, [applicant.first_name, applicant.last_name]))
        req.person_id = Applicant.generate_person_id(applicant.first_name, applicant.last_name, social, social_type)
        req.last_4 = str(social)[-4:]


=======
        req.name = ' '.join(filter(None, [applicant.first_name, applicant.last_name]))

        # call out to generate_person_id
        req.person_id = Applicant.generate_person_id(applicant.first_name, applicant.last_name, social)

        # encrypt social data
>>>>>>> 6d09c91465d6fab398823b65389a593e2e43b713
        req.social_data, req.social_data_key = settings.SOCIAL_CIPHER.encrypt_long_encoded(social)

        # credit settings
        req.bureaus = settings.CREDIT_BUREAUS
        req.approved_at_beacon = settings.CREDIT_APPROVED_BEACON
        req.stop_running_at_beacon = settings.STOP_RUNNING_AT_BEACON

        # save and return
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
    status_string = models.CharField(max_length=20)
<<<<<<< HEAD

    status_string = models.CharField(max_length=20)
=======
>>>>>>> 6d09c91465d6fab398823b65389a593e2e43b713

    # bookkeeping
    transaction_id = models.CharField(max_length=64)
    transaction_status = models.CharField(max_length=20)

    # address
    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=10)
    country_code = models.CharField(max_length=10)


    def __unicode__(self):

        return "CreditFile(name=%r, bureau=%r, beacon=%r, status_string=%r)" % (
            self.name, self.bureau, self.beacon, self.status_string)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('name', 'bureau', 'fraud', 'frozen', 'nohit', 'vermont', 'beacon', 'generated_date', 'status_string')
        }
        return jsonable

<<<<<<< HEAD
=======
    #@property
    #def another_status_string(self):
    #    if self.fraud or self.frozen or self.vermont:
    #        return 'REVIEW'
    #    if self.nohit:
    #        return 'NO HIT'
    #    if self.beacon >= settings.CREDIT_APPROVED_BEACON:
    #        return 'APPROVED'
    #    return 'DCS'


>>>>>>> 6d09c91465d6fab398823b65389a593e2e43b713
    class Meta:
        verbose_name = "Credit File"
        app_label = 'agreement'


