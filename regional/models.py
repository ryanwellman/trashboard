from django.db import models


class Region(models.Model):
    zipcode = models.CharField(max_length=10)
    city = models.CharField(max_length=80)
    county = models.CharField(max_length=80)
    state = models.CharField(max_length=2)
    areacode = models.CharField(max_length=3)

    def exists_in(self, dict):
        if self.state in dict.get('state', {}):
            return 'state', self.state
        if (self.city, self.state) in dict.get('city', {}):
            return 'city', (self.city, self.state)
        if (self.county, self.state) in dict.get('county', {}):
            return 'county', (self.county, self.state)
        if self.zipcode in dict.get('zipcode', {}):
            return 'zipcode', self.zipcode
        return False

    def get_pretty_name(self, region_type):
        if region_type == 'state':
            return 'the state of %s' % self.state
        if region_type == 'city':
            return 'the city of %s, %s' % (self.city, self.state)
        if region_type == 'county':
            return '%s County, %s' % (self.county, self.state)

        return 'the zip code %s' % self.zipcode

    @classmethod
    def filter_by_zipcode(kls, zipcode):
        zipcode = zipcode[:5]
        return kls.objects.filter(zipcode=zipcode)

    @classmethod
    def get_by_zipcode(kls, zipcode):
        zipcode = zipcode[:5]
        return kls.objects.get(zipcode=zipcode)
