from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from org.models import Organization, OrgUser


class OrganizationBackend(ModelBackend):

    supports_object_permissions = True

    def authenticate(self, org_code=None, username=None, password=None):

        if org_code is None:
            return None

        try:
            organization = Organization.objects.get(org_code__iexact=org_code)
            print "org found"
        except Organization.DoesNotExist:
            print "org not found"
            return None

        try:
            orguser = OrgUser.objects.get(organization=organization,
                                          username__iexact=username,
                                          django_user__is_active=True)
            print "orguser found"
            if orguser.django_user.check_password(password):
                print "password good"
                return orguser.django_user
            print "password bad", password

        except OrgUser.DoesNotExist:
            print "orguser not found"
            return None

