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

        # find the m2m model types and instances thereof
        m2mtypes = dict((f.name, f.rel.to) for f in self._meta.many_to_many)
        m2minstances = dict((f, getattr(self, f).all()) for f in m2mtypes)

        # now find the through table types and instances (they have a _set)
        throughtypes = dict((f.name, f.rel.through) for f in self._meta.many_to_many)
        throughnames = dict((f.name, f.m2m_db_table().rsplit('_')[1]) for f in self._meta.many_to_many)
        throughinstances = dict((throughnames[f], getattr(self, throughnames[f] + "_set").all()) for f in throughnames)

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

                    # update and add it to the original object
                    new_field.update_from_dict(incoming.get(k))
                    setattr(self, k, new_field)
                elif k in m2minstances:
                    # does it exist?
                    # at this point incoming[k] should be a list (json array) of dicts
                    if type(incoming[k]) is not list:
                        # incoming[k] = list(incoming[k])
                        print "many to many relationships require an array to update from"
                        raise TypeError
                    if m2minstances[k] is None:
                        # create a new through table instance and save it with the right fk refs
                        new_field = m2mtypes[k]()
                        new_through = throughtypes[k]() # needs to have its m2m fields set to mean anything
                    else:
                        # use the existing ones as these should be lists now
                        new_field = m2minstances[k]
                        new_through = throughinstances[throughnames[k]]

                    # update them and add them to the original object
                    for field in incoming.get(k):
                        new_field.update_from_dict(field)
                        new_through.update_from_dict(field) # no need to save here
                else:
                    setattr(self, k, incoming.get(k))

        # now save it for it to persist
        self.save()

    def serialize(self, ignore=[], ignorefk=False, ignorem2m=False):
        """
        convert this model into a dictionary that is easily json-able
        along with all of its other foreign keyed models
        you are able to specify fields to ignore
        """

        # this method serializes from actual objects now
        assert type(ignore) is list

        # do the same thing as above
        fktypes = dict((f.name, f.rel.to) for f in self._meta.fields if f.get_internal_type() == 'ForeignKey')
        fkinstances = dict((f, getattr(self, f)) for f in fktypes)
        m2mtypes = dict((f.name, f.rel.to) for f in self._meta.many_to_many)
        m2minstances = dict((f, getattr(self, f).all()) for f in m2mtypes)
        throughtypes = dict((f.name, f.rel.through) for f in self._meta.many_to_many)
        throughnames = dict((f.name, f.m2m_db_table().rsplit('_')[1]) for f in self._meta.many_to_many)
        throughinstances = dict((throughnames[f], getattr(self, throughnames[f] + "_set").all()) for f in throughnames)

        # let's make the first one without ignored, the private leading _ stuff or foreign keys
        # these values are all strings as far as json is concerned
        plain = dict((k, str(v)) for k, v in self.__dict__.iteritems() if v is not None and k not in ignore and not k.startswith('_') and not k.endswith('_id'))

        # now let's get the related foreign key items from the _meta
        if ignorefk:
            fancy = {}
        else:
            fancy = dict((k, v.serialize()) for k, v in fkinstances.iteritems() if v is not None and k not in ignore)

        # the m2m items and their through table items
        # v should be an array since these are m2m
        # we should also ignore the reverse m2m links in the m2ms and the fk links in the through tables
        if ignorem2m:
            voodoo = {}
        else:
            voo = dict((k, [a.serialize(ignorem2m=True) for a in v]) for k, v in m2minstances.iteritems() if v is not None and k not in ignore)
            doo = dict((k, [a.serialize(ignorefk=True) for a in v]) for k, v in throughinstances.iteritems() if v is not None and k not in ignore)
            voodoo = dict(voo, **doo)

        # hax: fastest way to concatenate these
        return dict(dict(plain, **fancy), **voodoo)

    class Meta:
        abstract = True