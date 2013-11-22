import datetime
from django.core.exceptions import ValidationError
from django.db import models

class UpdatableAndSerializable(models.Model):
    """
    mixin for the update_from_dict and serialize functions to be available
    to base django models and makes them iterable
    """

    def __iter__(self):
        # iterate through the field names in the django model meta and pluck the next one out
        # this returns a tuple (fieldname, value) ripe for a generator expression
        fields = [field.name for field in self._meta.fields]
        for i in fields:
            yield (i, getattr(self, i))

    def update_from_dict(self, incoming, fields=[]):
        """
        allows you to update the fields of a model from an incoming dictionary
        optionally specifying a list of fields to update instead
        """        
        assert type(incoming) is dict
        assert type(fields) is list

        # throw out any field in fields that isn't in incoming or are id fields
        # but still only update fields you ask to update if fields is set
        # assign iterator to incoming if there are no fields
        if fields:
            iterator = [field for field in fields if field in incoming and field is not 'id']
        else:
            iterator = [field for field in iterator if field is not 'id']

        # find this model's foreign keyed model types and instances thereof
        # XXX: make this support m2m relationships
        fktypes = dict((f.name, f.rel.to) for f in self._meta.fields if f.get_internal_type() == 'ForeignKey')
        fkinstances = dict((f, getattr(self, f)) for f in fktypes)

        # save only fields that exist in the model and aren't id fields
        for k in iterator:
            if hasattr(self, k):
                if k is 'id':
                    continue
                # check to see if this requires recursion
                if k in fkinstances:
                    # now check to see if this thing is None
                    if fkinstances[k] is None:
                        # if it is, then we create one of the right type
                        new_field = fktypes[k]()                        
                    else:
                        # if isn't then we need to use that one
                        new_field = fkinstances[k]

                    # update and add it to the original object
                    new_field.update_from_dict(incoming.get(k))
                    setattr(self, k, new_field)
                else:
                    setattr(self, k, incoming.get(k))

        # now save it for it to persist
        self.save()

    def serialize(self, ignore=[]):
        """
        convert this model into a dictionary that is easily json-able
        along with all of its other foreign keyed models
        """
        # __dict__ of a django model contains all the plain properties of a model along with
        # cached copies of foreign keyed objects and state of the object itself
        # this method serializes from the cache
        assert type(ignore) is list

        # let's make the first one without ignored, the private leading _ stuff or foreign keys
        # these values are all strings as far as json is concerned
        plain = dict((k, str(v)) for k, v in self.__dict__.iteritems() if v is not None and k not in ignore and not k.startswith('_') and not k.endswith('_id'))

        # now let's get the cached objects
        # we know that the real names we need are ones with no leading _ and trailing _cache
        # still ignore properties by their original names though
        fancy = dict((k[1:-6], v.serialize()) for k, v in self.__dict__.iteritems() if v is not None and k[1:-6] not in ignore and k.endswith('_cache'))

        # hax: fastest way to concatenate these
        # XXX: ignore id fields?
        return dict(plain, **fancy)

    class Meta:
        abstract = True


class Applicant(UpdatableAndSerializable):
    """
    represents a customer signing an agreement

    might need more fields
    """

    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    initial = models.CharField(max_length=1)
    phone = models.CharField(max_length=15)

    def __unicode__(self):
        if self.initial:
            mid = self.initial + '. '
        else:
            mid = ''
        return "{0} {1}{2}".format(self.fname, mid, self.lname)

    class Meta:
        verbose_name = "Applicant"


class Address(UpdatableAndSerializable):
    """
    represents a physical location as blessed by a major postal service
    """

    address = models.CharField(max_length=80)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=25)
    zip = models.CharField(max_length=10)
    country = models.CharField(max_length=10)

    def __unicode__(self):
        # address city, state, country zip
        # postal codes should go last (?)
        return "{0} {1}, {2}, {4} {3}".format(self.address, self.city, self.state, self.zip, self.country)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


class Agreement(UpdatableAndSerializable):
    """
    represents an agreement by a customer to buy our products

    this particular version of Agreement is a shim for the actual Agreement
    which exists in dashboard and may or may not be compatible with this one

    general field reference:
        campaign: who gets paid commission
        applicants: whose credit is going to be run
        addresses: where to bill and where the alarm is
        pricetable_date: what day's prices should be used
        invoice_lines: what did we sell them and how much did we say it cost
        email: how to contact the applicants about this agreement
        approved: what was their credit score like
        package: what box do we use
        shipping: who gets paid to transport the package
        monitoring: who gets paid to watch this system
    
    XXX: fields that depend on things in pricemodels.py are in but commented out
         since we are still adding fields to this as the form takes shape
    XXX: needs a harness to inject test data - making that soon
    """

    # campaign = models.ForeignKey(Campaign)
    applicant = models.ForeignKey(Applicant, related_name='main_applicant')
    coapplicant = models.ForeignKey(Applicant, related_name='co_applicant', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing')
    system_address =models.ForeignKey(Address, related_name='system')
    pricetable_date = models.DateField(auto_now_add=True) # automatically timestamped on creation
    # invoice_lines = models.ManyToManyField(InvoiceLine, through='InvAgreement', related_name='Invoice Lines')
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=10)
    package = models.CharField(max_length=10)
    shipping = models.CharField(max_length=10)
    monitoring = models.CharField(max_length=10)

    def __unicode__(self):
        if not self.id:
            id_display = u'Unsaved'
        else:
            id_display = unicode(self.id)
        return u','.join([id_display, unicode(self.applicant), self.approved, self.package, unicode(self.billing_address), unicode(self.system_address)]) # needs campaign_id

    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'