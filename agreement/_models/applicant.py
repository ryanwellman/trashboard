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

    def sync_person_id(self, social):
        if not (self.first_name or self.last_name) or not social:
            self.person_id = None
        self.person_id = Applicant.generate_person_id(self.first_name, self.last_name, social)

    def get_credit_status(self, social=None):
        if not self.person_id:
            return None

        # Do I have a credit file for me?
        from credit_file import CreditFile, CreditRequest
        cf = gooN(CreditFile, applicant=self)

        if cf:
            return cf.status_string

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
        credit_request = gooN(CreditRequest, applicant=self)

        if credit_request:
            if getattr(settings, 'MOCK_CREDIT', None):
                self.run_mock_credit(credit_request, social)
                return self.get_credit_status()

            return 'PENDING'

        # If I don't have a social, I can't start it.
        if not social:
            return None

        # Is the social I got passed in actually what's on this
        # agreement?  This should never not be true.
        sanity_check = self.person_id == Applicant.generate_person_id(self.first_name, self.last_name, social)
        if not sanity_check:
            # XXX this should probably be handled smarter.
            # I'd use an assert but I don't want to 500 here.
            return None



        rq = CreditRequest.create_request(applicant=self, social=social)

        # Mock credit run.
        if getattr(settings, 'MOCK_CREDIT', None):
            self.run_mock_credit(rq, social)
            return self.get_credit_status()

        return 'PENDING'

    def run_mock_credit(self, request, social=None):
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
        cf = gooN(CreditFile, applicant=self)
        if not cf:
            return None

        return cf.beacon



    @staticmethod
    def generate_person_id(first_name, last_name, social):
        if not social:
            return None

        if not first_name and not last_name:
            return None

        person_tuple = (first_name, last_name, social)
        person_tuple_str = repr(person_tuple)


        full_name = ' '.join(filter(None, [first_name, last_name]))
        person = full_name + '/' + social;
        person_id = sha256(person)
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
            self.sync_person_id(social)

        if updater:
            updater.errors.extend(errors)
        return errors


    class Meta:
        verbose_name = "Applicant"
        app_label = 'agreement'


