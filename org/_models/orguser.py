from django.db import models
from datetime import datetime
from organization import Organization
from django.db.models import Q, Model

from django.contrib.auth.models import User

class OrgUser(models.Model):
    organization = models.ForeignKey(Organization)
    username = models.CharField(max_length=32)
    # The django_user has the password.  If it doesn't exist, this orguser is inaccessible.
    django_user = models.ForeignKey(User, null=True, blank=True)

    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)

    roles = models.ManyToManyField('Role', blank=True)

    manager_pin = models.CharField(verbose_name="Manager PIN",
                                   max_length=4, blank=True, null=True)

    @staticmethod
    def build_django_username(org_code, username):
        # Gets the next available django username for this.
        # This has to be done because PA users recycle usernames.
        # IS01 might not be IS01 later.  The original one is deactivated, but still
        # has to exist.  The new one gets created.

        # now, we want to have a unique auth username,
        # so get all auth usernames that start with this one.
        # We then iterate over all of these, finding the first
        # unique suffix we can.
        base_username = "{0}.{1}".format(org_code, username)


        qs = User.objects.filter(username__istartswith=base_username)
        already_taken = [u[0] for u in qs.values_list('username')]
        already_taken = [username.lower() for username in already_taken]

        z = 0
        candidate = base_username
        while candidate in already_taken:
            z += 1
            candidate = base_username + '.%02d' % z

        return candidate

    def save(self, *args, **kwargs):
        # If the username has changed, we need to make sure
        # the underlying user.username is updated.

        old_version = gooN(OrgUser, pk=self.pk) if self.pk else None
        if not self.django_user:
            self.django_user = User()

        django_username = OrgUser.build_django_username(org_code=self.organization.org_code, username=self.username)
        if self.django_user.username != django_username:
            self.django_user.username = django_username
            self.django_user.save()

        super(OrgUser, self).save(*args, **kwargs)

    def generate_pin(self):

        orgusers = OrgUser.objects.filter(organization=self.organization,
                                         manager_pin__isnull=False)
        current_pins = [ou[0] for ou in orgusers.values_list('manager_pin')]
        current_pins = list(set(current_pins))

        while True:
            pin = random.randint(1000, 9999)
            if str(pin) not in current_pins or len(current_pins) >= 9999-1000+1:
                break


        self.save()

    def bust_cache(self):
        self.cached_permissions = None

    @property
    def org_permissions(self):
        if getattr(self, 'cached_permissions', None):
            return self.cached_permissions

        self.cached_permissions = defaultdict(lambda org_code: [])
        lines = self.values('role__organization__org_code', 'role__applies_globally', 'role__permissions__codename')
        for line in lines:
            org_code = line['role__organization__org_code']
            codename = line['role__permissions__codename']
            if line['role__applies_globally']:
                self.cached_permissions['*'].append(codename)
            elif not org_code:
                self.cached_permissions[self.organization_id].append(codename)
            else:
                self.cached_permissions[org_code].append(codename)


        return self.cached_permissions


    def has_organization_permission(self, organization, permission_name):
        if isinstance(organization, [str, unicode]):
            org_code = organization

        # org_code is organization.org_code or organization (I passed a string)
        org_code = getattr(organization, org_code, organization)


        return permission_name in self.org_permissions[org_code]


        pass


    @property
    def full_name(self):
        return ' '.join(filter(None, [self.first_name, self.last_name])).strip()


    @property
    def display_name(self):
        return '{0} - {1}'.format(self.username, self.full_name)

    def __unicode__(self):
        fmt = '{0} @ {1}'
        if self.full_name:
            return fmt.format(self.full_name, self.organization)
        else:
            return fmt.format(self.username, self.organization)


    class Meta:
        app_label = 'org'
