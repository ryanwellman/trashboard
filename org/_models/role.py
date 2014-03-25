from django.db import models
from datetime import datetime
from organization import Organization
from django.db.models import Q, Model

from django.contrib.auth.models import User, Permission

class Role(models.Model):
    role_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=80)
    organization = models.ForeignKey(Organization, null=True, blank=True)  # When null, applies to user's org.
    permissions = models.ManyToManyField(Permission, blank=True)
    applies_globally = models.BooleanField(default=False) # when true, applies to all orgs.


    def __unicode__(self):
        return '{0} {1}'.format(self.organization, self.name)

    class Meta:
        #unique_together = [('name', 'organization')]
        ordering = ['name']
        app_label = 'org'


