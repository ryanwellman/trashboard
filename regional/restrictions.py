from decimal import Decimal

from django.conf import settings

from .models import Region
from datetime import datetime
from dateutil.parser import parse as parsedate


class erange(object):
    def __contains__(self, dt):
        if self.From is not None and dt < self.From:
            return False
        if self.To is not None and dt >= self.To:
            return False
        return True

    def __init__(self, From, To):
        self.From = From
        self.To = To


def coerce_to_date(x):
    if isinstance(x, tuple):
        return datetime(*x)
    if isinstance(x, str):
        return parsedate(x)
    if isinstance(x, datetime):
        return x
    return None


class dtrange(erange):
    def __init__(self, From, To):
        From = coerce_to_date(From)
        To = coerce_to_date(To)
        super(dtrange, self).__init__(From=From, To=To)


class RequirementsData(object):
    def __init__(self, region_type, region_name, **kwargs):
        #from_date, to_date, region_type, region_name, override_type, override_name, property_type, needs_form, fee
        #permit_url,
        # no_self_install, no_tech_install
        self.region_type = region_type
        self.region_name = region_name
        self.property_type = kwargs.get('property_type')

        self.from_date = kwargs.get('from_date')
        self.to_date = kwargs.get('to_date')
        self.dt = dtrange(self.from_date, self.to_date)

        self.override_type = kwargs.get('override_type')
        self.override_name = kwargs.get('override_name')

        self._permit_fee = kwargs.get('permit_fee')
        self.permit_url = kwargs.get('permit_url')

        self.addendum_fee = kwargs.get('addendum_fee')
        self.addendum_template = kwargs.get('addendum_template')

        self.no_tech_install = kwargs.get('no_tech_install')
        self.no_self_install = kwargs.get('no_self_install')

        # Prorate Fee quarters definition
        self.prorate_quarters = kwargs.get('prorate_quarters',
                                           (1,1,1,2,2,2,3,3,3,4,4,4))

        self.permit_notice = kwargs.get('permit_notice')

    @property
    def permit_fee(self):
        if isinstance(self._permit_fee, dict):
            asof = self.prorate_asof if self.prorate_asof else datetime.today()
            quarter = self.prorate_quarters[asof.month]
            return self._permit_fee[quarter]
        else:
            return self._permit_fee

    @permit_fee.setter
    def permit_fee(self, value):
        self._permit_fee = value

    def has_permit(self):
        return bool(self.permit_fee or self.permit_url)

    def has_addendum(self):
        return bool(self.addendum_fee or self.addendum_template)

    def matches(self, region_type, region_name, property_type, date):
        if self.region_type != region_type:
            return False
        if region_type != 'zipcode':
            if region_name != self.region_name:
                return False
        else:
            if region_name not in self.region_name:
                return False
        if self.property_type and self.property_type != property_type:
            return False
        if date not in self.dt:
            return False
        return True

PR = RequirementsData

PERMITS = [

    PR('city', ('Huntsville', 'AL'), permit_fee=10, no_self_install=True),
    # Zipcodes surrounding Huntsville, AL
    PR('zipcode', ['35741', '35749', '35756', '35757', '35758', '35759', '35763', '35671', '35773'],
        permit_fee=10,
        no_self_install=True,
        override_name=('Huntsville', 'AL'),
        override_type='city'),

    # No install locations
    PR('city', ('Antioch', 'IL'), no_self_install=True, no_tech_install=True),
    PR('city', ('Quincy', 'IL'), no_self_install=True, no_tech_install=True),
    PR('county', ('Sedgwick', 'KS'), no_self_install=True, no_tech_install=True),
    PR('county', ('Fayette', 'KY'), no_self_install=True, no_tech_install=True),
    PR('state', 'PR', no_self_install=True, no_tech_install=True),

    # No tech install locations
    PR('state', 'AK', no_tech_install=True),
    PR('state', 'DC', no_tech_install=True),
    PR('state', 'HI', no_tech_install=True),
    PR('state', 'MA', no_tech_install=True),
    PR('state', 'ME', no_tech_install=True),
    PR('state', 'MN', no_tech_install=True),
    PR('state', 'MT', no_tech_install=True),
    PR('state', 'NV', no_tech_install=True),
    PR('state', 'NY', no_tech_install=True),
    PR('state', 'OR', no_tech_install=True),
    PR('state', 'RI', no_tech_install=True),
    PR('state', 'WA', no_tech_install=True),
    PR('state', 'WY', no_tech_install=True),
    PR('city', ('Alton', 'IL'), no_tech_install=True),
    PR('city', ('Chickasaw', 'AL'), no_tech_install=True),
    PR('city', ('Carnation', 'WA'), no_tech_install=True),
    PR('city', ('Louisville', 'KY'), no_tech_install=True),
    PR('city', ('University Place', 'WA'), no_tech_install=True),
    PR('city', ('Country Club Hills', 'IL'), no_tech_install=True),
    PR('county', ('Charles', 'MD'), no_tech_install=True),

    # No self install (also Huntsville, above)
    PR('city', ('Broken Arrow', 'OK'), no_self_install=True),

    # No commercial install in ID
    PR('state', 'ID', property_type='commercial', no_self_install=True, no_tech_install=True),
    PR('city', ('Savannah', 'GA'), property_type='residential', permit_fee=12),
    PR('city', ('Savannah', 'GA'), property_type='commercial', permit_fee=24),

    # Miami by zipcodes, not by city name
    PR('zipcode', ['33125', '33126', '33127', '33128', '33129', '33130', '33131', '33132',
                   '33133', '33134', '33135', '33136', '33137', '33138', '33139', '33142',
                   '33144', '33145', '33146', '33147', '33150'],
       override_name=('Miami', 'FL'),
       override_type='city',
       permit_fee=82.50),

    PR('city', ('Avondale', 'AZ'), permit_fee=0, permit_url='permits/AZ/city-avondale-all.pdf'),
    PR('city', ('Phoenix', 'AZ'), permit_fee=17, permit_url='permits/AZ/city-phoenix-all.pdf'),
    PR('city', ('Maricopa', 'AZ'), permit_fee=10, permit_url='permits/AZ/city-maricopa-all.pdf'),
    PR('city', ('Citrus Heights', 'CA'), permit_fee=50, permit_url='permits/CA/city-citrus-heights-all.pdf'),
    PR('city', ('Elk Grove', 'CA'), permit_fee=50, permit_url='permits/CA/city-elk-grove-all.pdf'),
    PR('city', ('Novato', 'CA'), permit_fee=28, permit_url='permits/CA/city-novato-all.pdf'),
    PR('city', ('Redding', 'CA'), permit_fee=0, permit_url='permits/CA/city-redding-all.pdf'),
    PR('city', ('Roseville', 'CA'), permit_fee=35, permit_url='permits/CA/city-roseville-all.pdf'),

    PR('city', ('Sacramento', 'CA'), permit_fee=40, permit_url='permits/CA/city-sacramento-all.pdf',
       from_date=datetime(1970, 01, 01, 00, 00, 00), to_date=datetime(2013, 8, 6, 23, 59, 59)),
    PR('city', ('Sacramento', 'CA'), permit_fee=30, permit_url='permits/CA/city-sacramento-all.pdf'),
    PR('city', ('Cape Coral', 'FL'), permit_fee=25, permit_url='permits/FL/city-cape-coral-all.pdf'),
    PR('city', ('Gainesville', 'FL'), permit_fee=19.50, permit_url='permits/FL/city-gainesville-all.pdf'),
    PR('city', ('Albany', 'GA'), permit_fee=0, permit_url='permits/GA/city-albany-all.pdf'),
    PR('city', ('Lafayette', 'LA'), permit_fee=20, permit_url='permits/LA/city-lafayette-all.pdf'),
    PR('city', ('Bethlehem', 'PA'), property_type='residential', permit_fee=25, permit_url='permits/PA/city-bethlehem-all.pdf'),
    PR('city', ('Bethlehem', 'PA'), property_type='commercial', permit_fee=0,
       from_date=datetime(1970, 01, 01, 00, 00, 00), to_date=datetime(2013, 8, 6, 23, 59, 59)),
    PR('city', ('Bethlehem', 'PA'), property_type='commercial', permit_fee=50, permit_url='permits/PA/city-bethlehem-all.pdf'),
    PR('city', ('Lynchburg', 'VA'), permit_fee=0, permit_url='permits/VA/city-lynchburg-all.pdf'),
    PR('city', ('Suffolk', 'VA'), permit_fee=0, permit_url='permits/VA/city-suffolk-all.pdf'),
    PR('city', ('Auburn', 'WA'), permit_fee=24, permit_url='permits/WA/city-auburn-all.pdf'),
    PR('city', ('Issaquah', 'WA'), permit_fee=24, permit_url='permits/WA/city-issaquah-all.pdf'),
    PR('city', ('Lakewood', 'WA'), permit_fee=24, permit_url='permits/WA/city-lakewood-all.pdf'),
    PR('city', ('Kennewick', 'WA'), permit_fee=0,
       from_date=datetime(1970, 01, 01, 00, 00, 00), to_date=datetime(2013, 8, 6, 23, 59, 59)),
    PR('city', ('Kennewick', 'WA'), permit_fee=40, permit_url='permits/WA/city-kennewick-all.pdf'),
    PR('city', ('Santa Rosa', 'CA'), property_type='residential', permit_fee=10, permit_url='permits/CA/city-santa-rosa-all.pdf'),
    PR('city', ('Santa Rosa', 'CA'), property_type='commercial', permit_fee=15, permit_url='permits/CA/city-santa-rosa-all.pdf'),
    PR('city', ('Olympia', 'WA'), property_type='residential', permit_fee=25, permit_url='permits/WA/city-olympia-all.pdf',
       addendum_fee=0, addendum_template='addendums/city/wa-olympia.html'),
    PR('city', ('Olympia', 'WA'), property_type='commercial', permit_fee=35, permit_url='permits/WA/city-olympia-all.pdf',
       addendum_fee=0, addendum_template='addendums/city/wa-olympia.html'),
    PR('city', ('Dallas', 'TX'), property_type='residential', permit_fee=50, permit_url='permits/TX/city-dallas-all.pdf'),
    PR('city', ('Dallas', 'TX'), property_type='commercial', permit_fee=100, permit_url='permits/TX/city-dallas-all.pdf'),
    PR('city', ('San Diego', 'CA'), property_type='residential', permit_fee=100.25, permit_url='permits/CA/city-san-diego-all.pdf'),
    PR('city', ('San Diego', 'CA'), property_type='commercial', permit_fee=173.25, permit_url='permits/CA/city-san-diego-all.pdf'),
    PR('city', ('Oakland', 'CA'), property_type='residential', permit_fee=25, permit_url='permits/CA/city-oakland-all.pdf'),
    PR('city', ('Oakland', 'CA'), property_type='commercial', permit_fee=35, permit_url='permits/CA/city-oakland-all.pdf'),
    PR('city', ('Buffalo', 'NY'), permit_fee=20, permit_url='permits/NY/city-buffalo-all.pdf'),
    PR('city', ('Saint Louis', 'MO'), property_type='residential', permit_fee=110, permit_url='permits/MO/city-saint-louis-all.pdf',
       addendum_fee=0, addendum_template='addendums/city/mo-saint-louis.html'),
    PR('city', ('Saint Louis', 'MO'), property_type='commercial', permit_fee=135, permit_url='permits/MO/city-saint-louis-all.pdf',
       addendum_fee=0, addendum_template='addendums/city/mo-saint-louis.html'),
    PR('city', ('Alton', 'IL'), property_type='residential', permit_fee=25, permit_url='permits/IL/city-alton-all.pdf'),
    PR('city', ('Alton', 'IL'), property_type='commercial', permit_fee=50, permit_url='permits/IL/city-alton-all.pdf'),
    PR('city', ('East Saint Louis', 'IL'), property_type='residential', no_tech_install=True,
       permit_fee=25, permit_url='permits/IL/city-east-saint-louis-all.pdf'),
    PR('city', ('East Saint Louis', 'IL'), property_type='commercial', no_tech_install=True,
       permit_fee=50, permit_url='permits/IL/city-east-saint-louis-all.pdf'),
    PR('city', ('West Des Moines', 'IA'), property_type='residential', permit_fee=22, permit_url='permits/IA/city-west-des-moines-all.pdf'),
    PR('city', ('West Des Moines', 'IA'), property_type='commercial', permit_fee=34, permit_url='permits/IA/city-west-des-moines-all.pdf'),


### CITY ADDENDUMS
    PR('city', ('Fontana', 'CA'), addendum_fee=5, addendum_template='addendums/city/ca-fontana.html'),
    PR('city', ('Fremont', 'CA'), addendum_fee=5, addendum_template='addendums/city/ca-fremont.html'),
    PR('city', ('Modesto', 'CA'), addendum_fee=5, addendum_template='addendums/city/ca-modesto.html'),
    PR('city', ('San Jose', 'CA'), addendum_fee=5, addendum_template='addendums/city/ca-san-jose.html'),
    PR('city', ('Turlock', 'CA'), addendum_fee=5, addendum_template='addendums/city/ca-turlock.html'),
    PR('city', ('Detroit', 'MI'), addendum_fee=5, addendum_template='addendums/city/mi-detroit.html'),
    PR('city', ('Henderson', 'NV'), addendum_fee=5, addendum_template='addendums/city/nv-henderson.html'),
    PR('city', ('Las Vegas', 'NV'), addendum_fee=5, addendum_template='addendums/city/nv-las-vegas.html'),
    PR('city', ('North Las Vegas', 'NV'), addendum_fee=5, addendum_template='addendums/city/nv-north-las-vegas.html'),
    PR('city', ('Eugene', 'OR'), addendum_fee=5, addendum_template='addendums/city/or-eugene.html'),
    PR('city', ('Salt Lake City', 'UT'), addendum_fee=5, addendum_template='addendums/city/ut-salt-lake-city.html'),
    PR('city', ('South Salt Lake City', 'UT'), addendum_fee=5, addendum_template='addendums/city/ut-south-salt-lake-city.html'),
    PR('city', ('Taylorsville', 'UT'), addendum_fee=5, addendum_template='addendums/city/ut-taylorsville.html'),
    PR('city', ('West Valley City', 'UT'), addendum_fee=5, addendum_template='addendums/city/ut-west-valley-city.html'),
    PR('city', ('Murray', 'UT'), addendum_fee=0, addendum_template='addendums/city/ut-murray.html',
       from_date=datetime(1970, 01, 01, 00, 00, 00), to_date=datetime(2013, 8, 6, 23, 59, 59)),
    PR('city', ('Murray', 'UT'), addendum_fee=5, addendum_template='addendums/city/ut-murray.html'),
    PR('city', ('Bellingham', 'WA'), addendum_fee=5, addendum_template='addendums/city/wa-bellingham.html'),
    PR('city', ('Burien', 'WA'), addendum_fee=5, addendum_template='addendums/city/wa-burien.html'),
    PR('city', ('Seattle', 'WA'), addendum_fee=6, addendum_template='addendums/city/wa-seattle.html'),
    PR('city', ('Tacoma', 'WA'), addendum_fee=6, addendum_template='addendums/city/wa-tacoma.html'),
    PR('city', ('Yakima', 'WA'), addendum_fee=5, addendum_template='addendums/city/wa-yakima.html'),
    PR('city', ('Milwaukee', 'WI'), addendum_fee=5, addendum_template='addendums/city/wi-milwaukee.html'),

##### COUNTY PERMITS
    PR('county', ('Monterey', 'CA'), permit_fee=50, permit_url='permits/CA/county-monterey-all.pdf'),
    PR('county', ('San Francisco', 'CA'), property_type='residential',
       permit_fee={1: 45, 2: 33, 3: 22, 4: 56}, permit_url='permits/CA/county-san-francisco-all.pdf'),
    PR('county', ('San Francisco', 'CA'), property_type='commercial',
       permit_fee={1: 70, 2: 52, 3: 35, 4: 87}, permit_url='permits/CA/county-san-francisco-all.pdf'),
    PR('county', ('Denver', 'CO'), permit_fee=25, permit_url='permits/CO/county-denver-all.pdf'),
    PR('county', ('Douglas', 'CO'), permit_fee=40, permit_url='permits/CO/county-douglas-all.pdf'),
    PR('county', ('Alachua', 'FL'), permit_fee=15, permit_url='permits/FL/county-alachua-all.pdf'),
    PR('county', ('Lee', 'FL'), permit_fee=25, permit_url='permits/FL/county-lee-all.pdf'),
    PR('county', ('Indian River', 'FL'), permit_fee=30, permit_url='permits/FL/county-indian-river-all.pdf'),
    PR('county', ('Chatham', 'GA'), permit_fee=0,
       from_date=datetime(1970, 01, 01, 00, 00, 00), to_date=datetime(2013, 8, 6, 23, 59, 59)),
    PR('county', ('Chatham', 'GA'), property_type='residential', permit_fee=12),
    PR('county', ('Chatham', 'GA'), property_type='commercial', permit_fee=24),
    PR('county', ('Dekalb', 'GA'), from_date=datetime(2013,1,2,0,0,0), permit_fee=5, permit_notice='There is a $5 alarm registration fee required in DeKalb County.  This registration must be renewed yearly.  Protect America will contact you yearly to collect the registration renewal fee.'),
    PR('county', ('Saint Tammany', 'LA'), permit_fee=0, permit_url='permits/LA/county-saint-tammany-all.pdf'),
    PR('county', ('Montgomery', 'MD'), permit_fee=30, permit_url='permits/MD/county-montgomery-all.pdf'),
    PR('county', ('Prince Georges', 'MD'), property_type='residential', permit_fee=0, permit_url='permits/MD/county-prince-georges-residential.pdf'),
    PR('county', ('Prince Georges', 'MD'), property_type='commercial', permit_fee=50, permit_url='permits/MD/county-prince-georges-commercial.pdf'),
    PR('county', ('Washington', 'MD'), permit_fee=0, permit_url='permits/MD/county-washington-all.pdf'),
    PR('county', ('Washoe', 'NV'), permit_fee=24, permit_url='permits/NV/county-washoe-all.pdf'),
    PR('county', ('Onondaga', 'NY'), permit_fee=30, permit_url='permits/NY/county-onondaga-all.pdf'),
    PR('county', ('Fairfax', 'VA'), permit_fee=25, permit_url='permits/VA/county-fairfax-all.pdf'),
    PR('county', ('Loudoun', 'VA'), property_type='residential', permit_fee=0, permit_url='permits/VA/county-loudoun-residential.pdf'),
    PR('county', ('Loudoun', 'VA'), property_type='commercial', permit_fee=0, permit_url='permits/VA/county-loudoun-commercial.pdf'),

    #### COUNTY ADDENDUMS
    PR('county', ('Los Angeles', 'CA'), addendum_fee=0, addendum_template='addendums/county/ca-los-angeles.html'),
    PR('county', ('Palm Beach', 'FL'), addendum_fee=0, addendum_template='addendums/county/fl-palm-beach.html'),
]


def GetMatchingPRs(region, property_type, asof):
    prs = []
    for pr in PERMITS:

        if pr.region_type == 'county':
            r_name = (region.county, region.state)
        elif pr.region_type == 'city':
            r_name = (region.city, region.state)
        elif pr.region_type == 'state':
            r_name = region.state
        elif pr.region_type == 'zipcode':
            r_name = region.zipcode

        # If the calculated r_name is not in the allowed pr.region_name
        if not isinstance(pr.region_name, list):
            region_names = [pr.region_name]
        else:
            region_names = pr.region_name
        if r_name not in region_names:
            continue

        # check time
        if pr.dt and asof not in pr.dt:
            continue
        # check ptype
        if pr.property_type and pr.property_type != property_type:
            continue

        # attach asof restriction_date to the pr for prorate, if used.
        pr.prorate_asof = asof

        prs.append(pr)

    return prs


def get_install_method_permissions(zipcode, property_type, restriction_date):
    permissions = {'self_install': True, 'tech_install': True}
    property_type = 'commercial' if property_type == 'COMMERCIAL' else 'residential'

    regions = Region.filter_by_zipcode(zipcode)
    for region in regions:
        prs = GetMatchingPRs(region, property_type, restriction_date)
        for pr in prs:
            if pr.no_tech_install:
                permissions['tech_install'] = False
            if pr.no_self_install:
                permissions['self_install'] = False

    return permissions

def get_available_install_methods(zipcode, property_type, restriction_date):
    methods = ['TECH', 'GUIDED']
    if not zipcode:
        return methods

    if not property_type:
        return methods

    permissions = get_install_method_permissions(zipcode, property_type, restriction_date)

    if not permissions['tech_install']:
        methods.remove('TECH')
    if not permissions['self_install']:
        methods.remove('GUIDED')

    return methods

def GetMatchingPRsByZip(zipcode, property_type, asof):
    # Get every region that this zipcode is part of.

    # Then return every PR that matches any of those regions and the date.
    regions = Region.filter_by_zipcode(zipcode)
    prs = []
    for region in regions:
        prs.extend(GetMatchingPRs(region, property_type, asof))

    # Deduplicate just in case.
    prs = list(set(prs))

    return prs

def get_permit(zipcode, property_type, restriction_date):
    regions = Region.filter_by_zipcode(zipcode)
    for region in regions:
        prs = GetMatchingPRs(region, property_type, restriction_date)
        for pr in prs:
            if not pr.has_permit():
                continue

            permit = dict(price=Decimal(str(pr.permit_fee)),
                          url="{0}{1}".format(settings.STATIC_URL, pr.permit_url),
                          region_type=pr.override_type or pr.region_type,
                          region_name=pr.override_name or pr.region_name,
                          permit_notice=pr.permit_notice)
            return permit

    return None


def get_addendum(zipcode, property_type, restriction_date):
    regions = Region.filter_by_zipcode(zipcode)
    for region in regions:
        prs = GetMatchingPRs(region, property_type, restriction_date)
        for pr in prs:
            if not pr.has_addendum():
                continue

            addendum = dict(price=Decimal(str(pr.addendum_fee)),
                            template=pr.addendum_template,
                            region_type=pr.override_type or pr.region_type,
                            region_name=pr.override_name or pr.region_name)
            return addendum

    return None


def can_sell_fire_detectors(zipcode, property_type, tech_install=False):
    # returns (True/False, 'reason why not or None')
    if property_type and property_type.upper() == 'COMMERCIAL':
        msg = " ".join(["Customers in a commercial property cannot purchase",
                        "fire sensors."])
        return False, msg
    if tech_install:
        msg = " ".join(["Fire sensors cannot be sold when a technician is",
                        "installing the system."])
        return False, msg

    # Fire sensors may not be sold here.
    no_install = {
        'county': (
            ('Eagle', 'CO'),
        ),
    }

    # Fire sensors may not be sold here without a technician install,
    no_self_install = {
    }

    # Fire sensors may not be sold here with a technician install.
    no_tech_install = {
    }

    regions = Region.filter_by_zipcode(zipcode) if zipcode else []
    for region in regions:

        if region.exists_in(no_install):
            region_type, _ = region.exists_in(no_install)
            msg = "Customers in %s cannot purchase fire sensors."
            msg = msg % region.get_pretty_name(region_type)
            return False, msg
        if tech_install and region.exists_in(no_tech_install):
            msg = ("Customers in this location cannot purchase fire sensors "
                   "if a technician will be installing it.")
            return False, msg
        if not tech_install and region.exists_in(no_self_install):
            msg = ("Customers in this location cannot purchase fire sensors "
                   "unless a technician will be installing it.")
            return False, msg
        if region.state == 'ME' and property_type != 'HOMEOWNER':
            msg = ("Customers in Maine must be homeowners to purchase fire "
                   "sensors.")
            return False, msg
    return True, ""

