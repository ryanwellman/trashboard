from django.db import models
from django.utils import timezone

class Serializable(models.Model):
    """
    serializer class that makes serialize functions available
    to base django models and makes them iterable over their fields
    """

    def __iter__(self):
        # iterate through the field names in the django model meta and pluck the next one out
        # this returns a tuple (fieldname, value) ripe for a generator expression

        # XXX: does not support through tables
        fields = [field.name for field in self._meta.fields]
        m2mfields = [field.name for field in self._meta.many_to_many]

        for i in fields:
            yield (i, getattr(self, i))

        for i in m2mfields:
            yield (i, getattr(self, i).all())


    def serialize(self, ignore=[], ignorefk=False, ignorem2m=False, ignorefkid=True):
        """
        convert this model into a dictionary that is easily json-able
        along with all of its other foreign keyed models
        you are able to specify fields to ignore along with ignoring m2m, fk, or fk id fields
        this allows you to send m2m through tables as just fk ids as well
        """

        # this method serializes from actual objects now
        assert type(ignore) is list

        # obtain the following lists of types and instances

        # forward foreign key
        fktypes = dict((f.name, f.rel.to) for f in self._meta.fields if f.get_internal_type() == 'ForeignKey')
        fkinstances = dict((f, getattr(self, f)) for f in fktypes)

        # forward m2m
        m2mtypes = dict((f.name, f.rel.to) for f in self._meta.many_to_many)
        m2minstances = dict((f, getattr(self, f).all()) for f in m2mtypes)

        # m2m through tables
        throughtypes = dict((f.name, f.rel.through) for f in self._meta.many_to_many)
        throughnames = dict((f.name, str(f.m2m_db_table().rsplit('_')[1])) for f in self._meta.many_to_many)
        throughinstances = {f.name: getattr(self, f.name).all() for f in self._meta.many_to_many}
        #throughinstances = dict((throughnames[f], getattr(self, throughnames[f] + "_set").all()) for f in throughnames)

        # let's make the first one without ignored and without django private items
        # these values are all strings as far as json is concerned
        plain = dict((k, unicode(v)) for k, v in self.__dict__.iteritems() if v is not None and k not in ignore and not k.startswith('_'))

        # now get rid of the foreign key ids if you want to
        if ignorefkid:
            plain = dict((k, v) for k, v in plain.iteritems() if not k.endswith('_id'))

        # now let's get the related foreign key items from the _meta
        if ignorefk:
            fancy = {}
        else:
            fancy = dict((k, v.serialize(ignore=ignore)) for k, v in fkinstances.iteritems() if v is not None and k not in ignore)

        # the m2m items and their through table items
        # v should be an array since these are m2m
        # we should also ignore the reverse m2m links in the m2ms and the reverse fk links in the through tables
        # the reason through tables don't ignore hidden id fields is because that is how you can pair them when all you have is json
        if ignorem2m:
            voodoo = {}
        else:
            voo = dict((k, [a.serialize(ignore=ignore, ignorem2m=True) for a in v]) for k, v in m2minstances.iteritems() if v is not None and k not in ignore)
            doo = dict((k, [a.serialize(ignore=ignore, ignorefk=True, ignorefkid=False) for a in v]) for k, v in throughinstances.iteritems() if v is not None and k not in ignore)
            voodoo = dict(voo, **doo)

        # hax: fastest way to concatenate these
        return dict(dict(plain, **fancy), **voodoo)

    def as_jsonable(self):
        copy = self.__dict__.copy()
        del copy['_state']
        return copy

    def as_json(self):
        from handy.jsonstuff import dumps
        return dumps(self.as_jsonable())


    class Meta:
        abstract = True


class Updatable(Serializable):
    """
    allows certain models to update themselves in the database from a json-like blob
    none of these have m2m relationships

    list of updatables:

        Applicant
        Address
        InvoiceLine
        Agreement

    """

    def update_from_dict(self, incoming, fields=[]):
        """
        allows you to update the fields of a model from an incoming dictionary
        optionally specifying a list of fields to update instead

        does not support m2m relationships
        """

        # pretend we're using a strongly typed language
        assert type(incoming) is dict
        assert type(fields) is list

        # let's enumerate the fields in incoming that should be iterated over later
        # throw out any field in fields that isn't in incoming or are id fields
        # but still only update fields you ask to update if fields is set
        # assign enumerator to incoming minus ids if there are no fields
        if fields:
            enumerator = [field for field in fields if field in incoming and field is not 'id']
        else:
            enumerator = [field for field in incoming if field is not 'id']

        # find this model's foreign keyed model types and instances thereof
        fktypes = dict((f.name, f.rel.to) for f in self._meta.fields if f.get_internal_type() == 'ForeignKey')
        fkinstances = dict((f, getattr(self, f)) for f in fktypes)

        # fix datetime field in Agreement
        # XXX: make this get the field by type instead
        if hasattr(self, 'pricetable_date'):
            incoming['pricetable_date'] = self.pricetable_date

        # save only fields that exist in the model and aren't id fields
        for k in enumerator:
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

                    # update and add it to the original object if it can be updated
                    if hasattr(new_field, 'update_from_dict'):
                        new_field.update_from_dict(incoming.get(k))
                    setattr(self, k, new_field)
                else:
                    setattr(self, k, incoming.get(k))

        # now save it for it to persist
        self.save()

    class Meta:
        abstract = True