from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable

from hashlib import sha256
from datetime import timedelta, datetime

from annoying.functions import get_object_or_None as gooN
from django.conf import settings
from handy import intor
from datetime import datetime


class Applicant(Updatable):
    """
    represents a customer signing an agreement

    might need more fields
    this field is updatable from a json-like blob
    """

    agreement = models.ForeignKey('Agreement', related_name='all_applicants')

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15)
    last_4 = models.CharField(max_length=4)

    person_id = models.CharField(max_length=64, blank=True, null=True)

    def sync_person_id(self, social, social_type):
        if not (self.first_name or self.last_name) or not social:
            self.person_id = None
        self.person_id = Applicant.generate_person_id(self.first_name, self.last_name, social, social_type)

    def get_credit_status(self, social=None):
        if not self.person_id:
            return None

        # Social is None, or a dictionary with keys 'social' and 'social_type'

        # Do I have a credit file for me?
        from credit_file import CreditFile, CreditRequest
        cfs = CreditFile.objects.filter(applicant=self)
        print "Found cfs: ", list(cfs)
        if cfs:
            status_strings = [cf.status_string for cf in cfs]
            for status in ('APPROVED', 'REVIEW', 'NO HIT', 'DCS'):
                if status in status_strings:
                    return status
            return 'ERROR'  # It's not possible for a credit file to not be one of those four.



        # I don't have a credit file for me,
        # so see if I can find and copy one.
        earliest_reusable = datetime.now() - settings.CREDIT_REUSABLE_SPAN
        reusable = list(CreditFile.objects.filter(person_id=self.person_id, generated_date__gte=earliest_reusable))

        if reusable:
            reusable.sort(key=lambda cf: cf.generated_date, reversed=True)
            reuse = reusable[0]
            cf = reuse.clone(applicant=self)

            # I found one and cloned it, now return its status_string.
            return cf.status_string

        # I don't have one, and I couldn't clone one, so I need to run.

        # but if I already made a request, I'm pending.
        credit_request = gooN(CreditRequest, applicant=self, processed=0, error=0)

        if credit_request:
            if getattr(settings, 'MOCK_CREDIT', None):
                self.run_mock_credit(credit_request, social['social'], social['social_type'])
                return self.get_credit_status()

            return 'PENDING'

        # If I don't have a social, I can't start it.
        if not social:
            if list(CreditRequest.objects.filter(applicant=self, error=1)):
                return 'ERROR'

            return None

        system_address = self.agreement.system_address
        if not system_address or not all([getattr(system_address, k, None) for k in ('street1', 'city', 'state', 'zip')]):
            return None



        # This will fail because system_address will be null, but this list will keep getting constructed and raise an error.
        # things_to_check =   [   self.agreement.system_address,
        #                         self.agreement.system_address.street1,
        #                         self.agreement.system_address.city,
        #                         self.agreement.system_address.state,
        #                         self.agreement.system_address.zip,
        #                     ]
        # # anyone home?
        # try:
        #     first_not_falsy = next((thing for thing in things_to_check if thing))
        # except StopIteration:
        #     return None


        # Is the social I got passed in actually what's on this
        # agreement?  This should never not be true.
        sanity_check = self.person_id == Applicant.generate_person_id(self.first_name, self.last_name, social['social'], social['social_type'])
        if not sanity_check:
            # XXX this should probably be handled smarter.
            # I'd use an assert but I don't want to 500 here.
            print "SANITY CHECK FAILED"
            print social
            return 'ERROR'



        rq = CreditRequest.create_request(applicant=self, social=social['social'], social_type=social['social_type'])

        # Mock credit run.
        if getattr(settings, 'MOCK_CREDIT', None):
            self.run_mock_credit(rq, social)
            return self.get_credit_status()

        return 'PENDING'

    def run_mock_credit(self, request, social, social_type):
        from credit_file import CreditFile

        name = ' '.join(filter(None, [self.first_name, self.last_name]))
        mock = CreditFile(applicant=self,
            person_id=self.person_id,
            name=name,
            last_4 = social[-4:],
            run_request=request,
            generated_date=datetime.now(),
            bureau='equifax',
            beacon=intor(social[-3:], 601),
            transaction_id='Mock Credit',
            transaction_status='Done'
        )
        mock.save()

    def get_beacon(self):
        if not self.person_id:
            return None

        # Do I have a credit file for me?
        from credit_file import CreditFile, CreditRequest
        cfs = CreditFile.objects.filter(applicant=self)
        beacons = [cf.beacon for cf in cfs]
        if not beacons:
            return None
        return max(beacons)



    @staticmethod
    def generate_person_id(first_name, last_name, social, social_type):
        if not social:
            return None

        if not first_name and not last_name:
            return None


        person_tuple = (first_name, last_name, social, social_type)
        person_tuple_str = repr(person_tuple)


        #full_name = ' '.join(filter(None, [first_name, last_name]))
        #person = full_name + '/' + social;
        person_id = sha256(person_tuple_str)
        return person_id.hexdigest()


    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.first_name, mid, self.last_name)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('first_name', 'last_name', 'initial', 'phone1', 'phone2', 'person_id')
        }
        jsonable['credit_status'] = self.get_credit_status()
        return jsonable

    def update_from_blob(self, blob, updater=None):
        errors = []
        for field in ('first_name', 'last_name', 'initial', 'phone1', 'phone2', 'last_4'):
            setattr(self, field, blob.get(field) or '')

        if 'social' in blob:
            social = blob.get('social')
            social_type = blob.get('social_type', 'US')
            self.last_4 = social[-4:]
            print "syncing social: %r, %r" % (social, social_type)
            self.sync_person_id(social, social_type)

        if updater:
            updater.errors.extend(errors)
        return errors


    class Meta:
        verbose_name = "Applicant"
        app_label = 'agreement'


