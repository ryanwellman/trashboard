from django.db import models
from datetime import datetime
from ..uas import Serializable, Updatable





class Applicant(Updatable):
    """
    represents a customer signing an agreement

    might need more fields
    this field is updatable from a json-like blob
    """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15)
    last_4 = models.CharField(max_length=4)

    def sync_person_id(self):
        self.person_id = Applicant.generate_person_id(self.__dict__)

    @staticmethod
    def generate_person_id(first_name, last_name, social):
        full_name = ' '.join(filter(None, [data['first_name'], data['last_name']]))


    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.first_name, mid, self.last_name)

    def as_jsonable(self):
        jsonable = {
            field: getattr(self, field)
            for field in ('first_name', 'last_name', 'initial', 'phone1', 'phone2', 'last_4')
        }
        return jsonable

    def update_from_blob(self, blob, updater=None):
        errors = []
        for field in ('first_name', 'last_name', 'initial', 'phone1', 'phone2', 'last_4'):
            setattr(self, field, blob.get(field) or '')

        if updater:
            updater.errors.extend(errors)
        return errors


    class Meta:
        verbose_name = "Applicant"
        app_label = 'agreement'


